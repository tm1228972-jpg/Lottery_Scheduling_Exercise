# Online source audit — 2026-11-23

This note records primary/authoritative pages fetched during preparation of the six requested assignments. Bibliographic fields and the exact claims below were checked against the linked pages on the date shown. It is not a substitute for the instructor's required citation style, and it does not imply that every statement in every draft has been independently peer-reviewed.

## Sources checked

1. **Waldspurger, Carl A., and William E. Weihl.** “Lottery Scheduling: Flexible Proportional-Share Resource Management.” *Proceedings of the First Symposium on Operating Systems Design and Implementation (OSDI ’94)*, November 1994. Author-hosted paper: <https://www.waldspurger.org/carl/papers/lottery-osdi94.pdf>.
   - Read the paper's abstract and Sections 2–5. The paper defines tickets and probabilistic proportional allocation; gives `p=t/T`, binomial win counts, and a geometric first-win waiting model; and discusses ticket transfers, inflation, currencies, and compensation tickets. It describes a Mach 3.0 prototype and historical experiments. Those historical prototype results are not results for the teaching simulator in this repository.
   - The paper says a nonzero-ticket client will “eventually” win. In the fixed-probability independent-draw model this is an almost-sure asymptotic statement; `P(no win in k draws)=(1-p)^k` is still positive for every finite `k`. Do not translate it into a deterministic finite waiting-time guarantee.
2. **Liu, C. L., and James W. Layland.** “Scheduling Algorithms for Multiprogramming in a Hard-Real-Time Environment.” *Journal of the ACM* 20(1), 46–61, January 1973. DOI: <https://doi.org/10.1145/321738.321743>. ACM record: <https://dl.acm.org/doi/10.1145/321738.321743>; NASA Technical Reports Server record 19730036159: <https://ntrs.nasa.gov/citations/19730036159>.
   - ACM's record confirmed the authors, journal, volume/issue, pages, date, and DOI. NASA's record confirms the title and summarizes the single-processor result: a fixed-priority utilization upper bound can be as low as 70% for large task sets, while dynamic priority based on current deadlines can attain full utilization. The reports state the classical EDF/RM utilization results only under their ideal task-model assumptions; the utilization-bound distinction (RM bound sufficient, not necessary) is explicit.
3. **Hoare, C. A. R.** “Monitors: an operating system structuring concept.” *Communications of the ACM* 17(10), 549–557, October 1974. DOI: <https://doi.org/10.1145/355620.361161>.
   - The ACM abstract describes monitors as an OS structuring method, introduces synchronization, discusses a semaphore implementation and proof rule, and lists readers/writers as an example.
4. **Courtois, Pierre-Jacques, F. Heymans, and David L. Parnas.** “Concurrent control with ‘readers’ and ‘writers’.” *Communications of the ACM* 14(10), 667–668, October 1971. DOI: <https://doi.org/10.1145/362759.362813>.
   - The ACM abstract confirms the shared-read/exclusive-write model and two different service goals: minimizing reader delay or allowing writing as early as possible. This source does not make semaphore fairness a universal primitive guarantee.
5. **Kawash, Jalal.** “Process Synchronization with Readers and Writers Revisited.” *Journal of Computing and Information Technology* 13(1), 43–51, 2005. DOI: <https://doi.org/10.2498/cit.2005.01.04>. Publisher page: <https://cit.fer.hr/index.php/CIT/article/view/1561>; accessible article copy: <https://hrcak.srce.hr/file/69328>.
   - The article discusses starvation in the reader-preference and writer-preference variants and presents a third semaphore-based solution with both reader and writer progress, proved using SPIN. This is a literature result, not a claim about every monitor or semaphore implementation.
6. **Dijkstra, Edsger W.** *Cooperating Sequential Processes*. Archive transcription of EWD 123: <https://www.cs.utexas.edu/~EWD/transcriptions/EWD01xx/EWD123.html>.
   - The transcription introduces the P/V synchronizing primitives and treats their indivisible operation as essential. The 1974 Hoare ACM record independently lists Dijkstra's “Cooperating Sequential Processes” in *Programming Languages* (1968); reference entries use that published-chapter metadata and link the archival transcription for access.
7. **Peterson, Gary L.** “Myths about the mutual exclusion problem.” *Information Processing Letters* 12(3), 115–116, June 1981. DOI: <https://doi.org/10.1016/0020-0190(81)90106-X>.
   - ScienceDirect confirmed title, author, journal, date, pages, and DOI. The full article is access-controlled on the checked page.
8. **Ridge, Tom.** “Operational Reasoning for Concurrent Caml Programs and Weak Memory Models.” In *Theorem Proving in Higher Order Logics (TPHOLs 2007)*, LNCS 4732, 278–293. DOI: <https://doi.org/10.1007/978-3-540-74591-4_21>.
   - Springer’s abstract describes verification of a Peterson implementation under operational semantics and a modified Peterson algorithm for weak memory. It supports the caution that textbook mutual-exclusion pseudocode is tied to memory-model assumptions; it is not a blanket proof that every Peterson implementation fails on every modern system.
9. **Joseph, Mathai, and Paritosh Pandya.** “Finding response times in a real-time system.” *The Computer Journal* 29(5), 390–395, 1986. DOI: <https://doi.org/10.1093/comjnl/29.5.390>.
   - Oxford Academic's record confirmed the citation metadata. The article page did not provide full text in this check; the drafts therefore do not rely on a new formula attributed solely to it.
10. **Python Standard Library — `threading`.** <https://docs.python.org/3/library/threading.html>.
    - The documentation was fetched to document the language/runtime context of the educational monitor. The code's fairness claim is based on its explicit queue/admission policy plus test results and stated assumptions, not on a claim that Python's primitive lock is FIFO.

## Scope and verification boundaries

- References 1–9 are research or archival sources; reference 10 is implementation documentation.
- The complete task set for Exercise 3 comes from the existing Exercise 3 branch's report and is retained as given. The in-repository simulator independently reproduces its trace; this is not independent empirical evidence about real hardware.
- The seeded Lottery output, schedule trace, thread tests, video duration, and PPTX structure are repository-produced artifacts. They must not be attributed to the papers above.
- The screenshot establishes a six-row assignment checklist and document-format columns, but the exact seminar regulations are not readable from the available copy. No seminar-rule compliance is claimed pending the original readable rules.
