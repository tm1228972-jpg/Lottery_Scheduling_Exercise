"""Fair, non-reentrant readers-writers monitor for instructional use.

Readers that are ahead of the next writer may enter as a batch. Once a writer
is queued, later readers do not bypass it. Progress assumes finite critical
sections and that Python threads waiting on the condition are eventually
scheduled. The class does not make arbitrary user code safe outside its
context-manager regions.
"""

from __future__ import annotations

from collections import deque
from contextlib import contextmanager
from threading import Condition, get_ident
from typing import Iterator


class FairReadersWritersMonitor:
    """A FIFO-by-phase readers-writers lock implemented with a monitor.

    The monitor protects its queue and active-owner state with one condition.
    Consecutive readers before the next writer are admitted together; a reader
    queued behind a writer waits until that writer and all earlier requests
    finish. Read-to-write upgrades, recursive reads, and recursive writes are
    intentionally unsupported.
    """

    def __init__(self) -> None:
        self._condition = Condition()
        self._queue: deque[tuple[int, str]] = deque()
        self._next_ticket = 0
        self._active_readers: set[int] = set()
        self._active_writer: int | None = None

    @property
    def active_readers(self) -> int:
        with self._condition:
            return len(self._active_readers)

    @property
    def writer_active(self) -> bool:
        with self._condition:
            return self._active_writer is not None

    @property
    def waiting_modes(self) -> tuple[str, ...]:
        """Queued request modes, primarily for observability and tests."""

        with self._condition:
            return tuple(mode for _, mode in self._queue)

    def acquire_read(self) -> None:
        owner = get_ident()
        with self._condition:
            if owner in self._active_readers:
                raise RuntimeError("recursive read acquisition is not supported")
            token = self._enqueue("R")
            while self._active_writer is not None or self._writer_before(token):
                self._condition.wait()
            self._remove(token)
            self._active_readers.add(owner)
            self._condition.notify_all()

    def release_read(self) -> None:
        owner = get_ident()
        with self._condition:
            if owner not in self._active_readers:
                raise RuntimeError("current thread does not hold a read lock")
            self._active_readers.remove(owner)
            self._condition.notify_all()

    def acquire_write(self) -> None:
        owner = get_ident()
        with self._condition:
            if self._active_writer == owner:
                raise RuntimeError("recursive write acquisition is not supported")
            if owner in self._active_readers:
                raise RuntimeError("read-to-write upgrade is not supported")
            token = self._enqueue("W")
            while (
                self._active_writer is not None
                or self._active_readers
                or not self._queue
                or self._queue[0][0] != token
            ):
                self._condition.wait()
            self._queue.popleft()
            self._active_writer = owner
            self._condition.notify_all()

    def release_write(self) -> None:
        owner = get_ident()
        with self._condition:
            if self._active_writer != owner:
                raise RuntimeError("current thread does not hold the write lock")
            self._active_writer = None
            self._condition.notify_all()

    @contextmanager
    def read_lock(self) -> Iterator[None]:
        self.acquire_read()
        try:
            yield
        finally:
            self.release_read()

    @contextmanager
    def write_lock(self) -> Iterator[None]:
        self.acquire_write()
        try:
            yield
        finally:
            self.release_write()

    def _enqueue(self, mode: str) -> int:
        token = self._next_ticket
        self._next_ticket += 1
        self._queue.append((token, mode))
        self._condition.notify_all()
        return token

    def _writer_before(self, token: int) -> bool:
        return any(ticket < token and mode == "W" for ticket, mode in self._queue)

    def _remove(self, token: int) -> None:
        for queued in tuple(self._queue):
            if queued[0] == token:
                self._queue.remove(queued)
                return
        raise RuntimeError("queued request disappeared before admission")
