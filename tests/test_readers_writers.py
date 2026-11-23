import threading
import time
import unittest

from lottery_lab import FairReadersWritersMonitor


def wait_until(predicate, timeout=2.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.001)
    return predicate()


class ReadersWritersMonitorTests(unittest.TestCase):
    def test_allows_concurrent_readers(self):
        monitor = FairReadersWritersMonitor()
        both_inside = threading.Event()
        release_readers = threading.Event()
        errors = []

        def reader():
            try:
                with monitor.read_lock():
                    if monitor.active_readers == 2:
                        both_inside.set()
                    if not release_readers.wait(2):
                        errors.append("reader timed out")
            except BaseException as error:  # surfaced in the main test thread
                errors.append(repr(error))

        threads = [threading.Thread(target=reader) for _ in range(2)]
        for thread in threads:
            thread.start()
        self.assertTrue(both_inside.wait(1), "readers were not admitted concurrently")
        release_readers.set()
        for thread in threads:
            thread.join(2)
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertEqual(errors, [])
        self.assertEqual(monitor.active_readers, 0)

    def test_writer_queued_before_reader_is_not_bypassed(self):
        monitor = FairReadersWritersMonitor()
        order = []
        writer_entered = threading.Event()
        release_writer = threading.Event()
        errors = []

        monitor.acquire_read()

        def writer():
            try:
                monitor.acquire_write()
                order.append("writer")
                writer_entered.set()
                if not release_writer.wait(2):
                    errors.append("writer release timed out")
                monitor.release_write()
            except BaseException as error:
                errors.append(repr(error))

        def reader():
            try:
                with monitor.read_lock():
                    order.append("reader")
            except BaseException as error:
                errors.append(repr(error))

        writer_thread = threading.Thread(target=writer)
        reader_thread = threading.Thread(target=reader)
        writer_thread.start()
        self.assertTrue(wait_until(lambda: monitor.waiting_modes == ("W",)))
        reader_thread.start()
        self.assertTrue(wait_until(lambda: monitor.waiting_modes == ("W", "R")))
        monitor.release_read()

        try:
            self.assertTrue(writer_entered.wait(1))
            self.assertEqual(order, ["writer"])
        finally:
            release_writer.set()
        writer_thread.join(2)
        reader_thread.join(2)
        self.assertFalse(writer_thread.is_alive())
        self.assertFalse(reader_thread.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(order, ["writer", "reader"])

    def test_rejects_release_without_ownership_and_unsupported_upgrade(self):
        monitor = FairReadersWritersMonitor()
        with self.assertRaises(RuntimeError):
            monitor.release_read()
        with self.assertRaises(RuntimeError):
            monitor.release_write()
        with monitor.read_lock():
            with self.assertRaises(RuntimeError):
                monitor.acquire_write()
            with self.assertRaises(RuntimeError):
                monitor.acquire_read()

    def test_writer_excludes_readers_and_other_writers(self):
        monitor = FairReadersWritersMonitor()
        state_guard = threading.Lock()
        state = {"readers": 0, "writer": False, "violations": []}
        start = threading.Barrier(7)

        def reader():
            start.wait()
            for _ in range(15):
                with monitor.read_lock():
                    with state_guard:
                        if state["writer"]:
                            state["violations"].append("reader overlapped writer")
                        state["readers"] += 1
                    time.sleep(0.0005)
                    with state_guard:
                        state["readers"] -= 1

        def writer():
            start.wait()
            for _ in range(10):
                with monitor.write_lock():
                    with state_guard:
                        if state["writer"] or state["readers"]:
                            state["violations"].append("writer overlapped another owner")
                        state["writer"] = True
                    time.sleep(0.0005)
                    with state_guard:
                        state["writer"] = False

        threads = [threading.Thread(target=reader) for _ in range(5)]
        threads += [threading.Thread(target=writer) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(5)
        self.assertFalse(any(thread.is_alive() for thread in threads), "lock made no progress")
        self.assertEqual(state["violations"], [])
        self.assertEqual(monitor.active_readers, 0)
        self.assertFalse(monitor.writer_active)


if __name__ == "__main__":
    unittest.main()
