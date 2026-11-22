# Readers-Writers Synchronization

The readers-writers problem allows concurrent readers but requires writers to have exclusive access. Correct solutions consider mutual exclusion, progress, bounded waiting, and starvation. Dekker's algorithm and Peterson's algorithm are classic software solutions for mutual exclusion between two processes under assumptions about atomic reads/writes and memory behavior; they are not directly general multi-reader/multi-writer solutions. Semaphores provide atomic wait/signal operations and can implement reader counters and writer locks. A readers-preference semaphore solution may starve writers if readers continuously arrive. Monitors encapsulate shared state and operations, using condition variables for waiting and notification; fairness still depends on the monitor policy.

| Mechanism | Scope | Main point |
|---|---|---|
| Dekker | Two processes | Software mutual exclusion |
| Peterson | Two processes | Intent flags plus turn |
| Semaphore | General | Flexible, but easy to misuse |
| Monitor | General | Encapsulation and condition variables |

English: Dekker/Peterson are classic two-process algorithms; semaphores and monitors are more suitable primitives for general readers-writers designs.
