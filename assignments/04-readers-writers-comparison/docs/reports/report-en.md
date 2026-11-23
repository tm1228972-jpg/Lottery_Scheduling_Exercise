# Exercise 4 — Dekker, Peterson, Semaphores, and Monitors (Short Research Draft)

> **Status:** This source-based working report is substantially shorter than the requested approximately 40-page bilingual final. No repeated filler has been added. Source metadata and the claims cited below were checked on 2026-11-23; see [the source-audit record](../../../../docs/research-source-audit.md). The DOCX/PDF are provisional exports.

## Abstract

Mutual exclusion protects shared state, but the mechanism used to obtain it affects progress, waiting, CPU use, and the kinds of programs it can express. Dekker's and Peterson's classic software protocols coordinate two participants using shared intent flags and a turn variable. Semaphores provide atomic wait/signal operations, while monitors encapsulate shared state and synchronization procedures. In the readers-writers problem, several readers may coexist, but a writer must be exclusive. Neither “semaphore” nor “monitor” implies fairness automatically: reader preference, writer preference, wake-up ordering, and queue discipline affect starvation. This report compares the algorithms at the level of their assumptions and guarantees, then describes a tested FIFO-by-phase Python monitor without presenting it as a proof for every interleaving.

## 1. Correctness questions for synchronization

A useful synchronization design states which of these properties it provides:

- **Mutual exclusion (safety):** forbidden critical-section overlaps never occur.
- **Progress:** if requests exist and the critical section can become free, some eligible request eventually proceeds; the system does not deadlock by refusing all progress.
- **Bounded waiting / bounded bypass:** after a process requests entry, the number of later entries that may overtake it is bounded.
- **Starvation freedom:** every continuously pending request eventually enters under stated scheduling and critical-section assumptions.
- **Time bound:** an explicit upper bound in seconds or clock ticks. Starvation freedom does not by itself provide such a real-time bound.

These are different properties. A lock may be mutually exclusive but unfair. A fair queue may guarantee a finite number of overtakes, yet not a time deadline if earlier critical sections or OS scheduling delays are unbounded. A test suite can expose bugs but cannot establish all these properties for every possible execution.

## 2. Readers-writers problem and service policies

The classical readers-writers resource allows multiple readers simultaneously because reads do not modify the shared object; a writer requires exclusive access. Courtois, Heymans, and Parnas formalized two variants with different goals: minimizing reader delay, or allowing writing to take place as early as possible [1]. These goals can favor opposite classes. Later analysis makes the starvation trade-off explicit: reader-preference can indefinitely delay writers when new readers continue to arrive; writer-preference can indefinitely delay readers during a sustained stream of writers [2].

A third, fair policy can require progress for both classes, but its guarantee depends on the admission/queue rules and the assumptions made about threads and critical-section duration. “Readers-writers lock” is therefore not a complete policy specification. A report should say which class can bypass which other class, whether readers enter in batches, and what scheduling assumption supports eventual progress.

## 3. Dekker's two-process algorithm

Dekker's algorithm is a classic software-only solution to mutual exclusion for two processes. With `flag[0]` and `flag[1]` initially false, each process raises its intent flag. If both want to enter, a shared `turn` variable resolves the conflict; the process that yields temporarily lowers its flag and retries after the turn changes.

```text
process i, where j = 1 - i:
    repeat:
        flag[i] ← true
        while flag[j]:
            if turn = j:
                flag[i] ← false
                while turn = j:
                    busy_wait
                flag[i] ← true
        critical_section
        turn ← j
        flag[i] ← false
        remainder_section
```

Under the textbook assumptions of atomic shared-variable reads/writes, sequentially consistent visibility, and two participants following the protocol, the flags prevent simultaneous entry while `turn` resolves the case in which both request the critical section. The algorithm allows progress when only one process requests entry and alternates priority after a process exits. Its nested retry logic is more complicated than Peterson's and it busy-waits. This is algorithmic pseudocode, not executable code from this repository.

## 4. Peterson's two-process algorithm

Peterson's protocol uses an intent flag per process and one `turn` variable:

```text
process i, where j = 1 - i:
    flag[i] ← true
    turn ← j
    while flag[j] and turn = j:
        busy_wait
    critical_section
    flag[i] ← false
    remainder_section
```

For two processes under the same ideal atomic/sequentially-consistent shared-memory model, the entry condition prevents both from passing the loop simultaneously. When both flags are raised, `turn` determines which yields. When only one flag is raised, the other process's flag is false and the requester can enter. The protocol is often used to teach mutual exclusion, progress, and bounded bypass, but it is not a direct solution for an arbitrary number of readers and writers.

The memory model is part of the correctness argument. Compilers and processors may reorder or delay ordinary loads/stores; a proof for sequentially consistent atomic variables does not automatically validate a literal translation with ordinary variables in a modern programming language. Ridge verifies a Peterson implementation and develops a modified protocol for weak memory, underscoring that implementation semantics matter [6]. This repository does not implement Dekker or Peterson as Python locks.

## 5. Semaphores

A semaphore is an integer-like synchronization object with atomic wait and signal operations, conventionally written `P`/`V` or `wait`/`signal`. Dijkstra's account emphasizes that these operations must act indivisibly [3]. A **binary semaphore** supports a single permit; a **counting semaphore** represents a nonnegative number of available permits. Implementations may block a thread when no permit is available; a semaphore abstraction does not, by its name alone, specify FIFO service.

A common reader-preference pattern uses a mutex to protect `read_count`. The first reader waits on the resource semaphore, each reader increments the count while protected by the mutex, and the last reader signals the resource. Writers wait on the same resource semaphore. This permits concurrent readers and exclusive writers, but new readers may continue joining an active reader phase and postpone a waiting writer. Reversing the gate to give writers preference can postpone readers instead. Kawash analyzes these two variants and presents a third semaphore-based algorithm with progress for both classes, proved with SPIN [2].

Semaphores are expressive and can be implemented with blocking rather than busy-waiting. They also expose ordering details to the programmer: mismatched wait/signal calls, wrong initialization, signalling the wrong condition, or relying on an unstated queue policy can cause deadlock, unsafe overlap, lost progress, or starvation.

## 6. Monitors and condition variables

A monitor groups shared state with procedures that operate on it. At most one thread executes a monitor procedure at a time under the monitor's mutual-exclusion rule; condition variables allow a procedure to wait for a predicate to become true. Hoare's paper develops monitors as an operating-system structuring concept, discusses synchronization and a semaphore implementation, and includes a readers-writers example [4].

Condition-variable semantics matter. In a Hoare-style signal-and-urgent-wait model, a signalled process immediately receives monitor control before the signaler continues. In Mesa-style implementations, signalling makes a waiter runnable but the signaler continues; the waiter later reacquires the monitor and must re-check its predicate in a loop. Code should therefore wait on conditions such as `while active_writer or earlier_writer_waiting: condition.wait()`, not assume that a wake-up proves admission. A monitor packages invariants and state, but its notification and entry-queue policy still determine fairness.

## 7. Comparison

| Mechanism | Intended scope | Waiting style | Correctness assumptions | Fairness / starvation issue |
|---|---|---|---|---|
| Dekker | Exactly two participants | Busy-wait | Atomic shared variables; sequential consistency; both follow protocol | Turn resolves simultaneous requests in the classic model; no real-time bound; busy-wait consumes CPU |
| Peterson | Exactly two participants | Busy-wait | Atomic shared variables; ordering/memory-model assumptions | Bounded bypass in the textbook model; naive translation may fail under weak memory |
| Semaphore | General permit/resource synchronization | Often blocking; implementation-dependent | Atomic `wait`/`signal`, correct initialization and pairing | Fairness depends on queue and wake-up policy; reader/writer preference can starve the opposite class |
| Monitor | General encapsulated shared state | Condition wait/blocking | Correct invariant, predicate loop, and signal discipline | Easier to centralize policy; FIFO admission is not automatic |

The table separates algorithmic scope from primitive power. Dekker and Peterson are two-process mutual-exclusion protocols; a multi-reader/one-writer service needs a higher-level design. Semaphores and monitors can implement that design, but the service policy must be spelled out.

## 8. Repository monitor and admission policy

`FairReadersWritersMonitor` uses a condition-protected FIFO request queue. Consecutive queued readers before the next writer may enter as one batch. A reader queued after a writer cannot pass it. A writer enters only after earlier requests and active readers finish. This avoids the unbounded stream of newly arriving readers bypassing an already queued writer, while preserving concurrent reading for a reader batch.

The implementation intentionally rejects recursive acquisition and read-to-write upgrades. Its progress statement assumes finite critical sections and that waiting threads are eventually scheduled. Queue order limits the number of later requests that can overtake a request; it is not a wall-clock deadline because thread scheduling and critical-section durations have no enforced maximum in this model. It uses Python's `Condition` to protect state; the report does not claim that Python's underlying primitive locks are FIFO.

Four tests check concurrent readers, exclusion between readers and writers, the no-bypass ordering for a queued writer, and unsupported ownership patterns. They are regression tests over selected schedules, not a model-checking proof. The implementation is educational and does not make arbitrary user code safe outside its context-manager regions.

## 9. Practical selection and common errors

Choose Dekker or Peterson to study the two-participant software mutual-exclusion problem under explicit memory assumptions, not as drop-in production locks. Use semaphores when permits or explicit wait/signal coordination match the problem and the queue policy is understood. Use a monitor when shared state and its invariants should be encapsulated with condition predicates. For readers-writers, document whether readers or writers receive preference, whether queued requests are FIFO, when a reader batch closes, and what progress assumptions apply.

Common mistakes include confusing mutual exclusion with fairness; claiming bounded time from starvation freedom; calling a test a proof; using `if` instead of rechecking a condition predicate; omitting atomicity/order assumptions for software-only algorithms; assuming every semaphore wakes the oldest waiter; and presenting a two-process algorithm as a general readers-writers lock.

## 10. Conclusion

Dekker and Peterson are compact, instructive two-process protocols. Semaphores are general atomic synchronization primitives, and monitors encapsulate shared state and condition waits. None of these names alone determines a fair readers-writers service. The admission policy and assumptions decide which class can progress and whether starvation is possible. The repository's FIFO-by-phase monitor illustrates one policy and tests several invariants, but is not a formal proof or a real-time lock.

## References

1. Courtois, Pierre-Jacques, F. Heymans, and David L. Parnas. “Concurrent control with ‘readers’ and ‘writers’.” *Communications of the ACM* 14(10), 667–668, October 1971. DOI: 10.1145/362759.362813.
2. Kawash, Jalal. “Process Synchronization with Readers and Writers Revisited.” *Journal of Computing and Information Technology* 13(1), 43–51, 2005. DOI: 10.2498/cit.2005.01.04.
3. Dijkstra, Edsger W. “Cooperating Sequential Processes.” In *Programming Languages*, edited by F. Genuys, Academic Press, 1968. Archival transcription: EWD 123.
4. Hoare, C. A. R. “Monitors: an operating system structuring concept.” *Communications of the ACM* 17(10), 549–557, October 1974. DOI: 10.1145/355620.361161.
5. Peterson, Gary L. “Myths about the mutual exclusion problem.” *Information Processing Letters* 12(3), 115–116, June 1981. DOI: 10.1016/0020-0190(81)90106-X.
6. Ridge, Tom. “Operational Reasoning for Concurrent Caml Programs and Weak Memory Models.” In *Theorem Proving in Higher Order Logics (TPHOLs 2007)*, LNCS 4732, 278–293. DOI: 10.1007/978-3-540-74591-4_21.
7. Python Software Foundation. “`threading` — Thread-based parallelism.” Python Standard Library documentation.

Full URLs are in the [reference list](../../references.md). Source audit: [evidence and claim limits](../../../../docs/research-source-audit.md).
