# References — Exercise 4: Mutual Exclusion and Readers/Writers

Metadata and the cited source claims were checked online on 2026-11-23. See [`../../docs/research-source-audit.md`](../../docs/research-source-audit.md) for claim-by-claim notes.

1. Courtois, Pierre-Jacques, F. Heymans, and David L. Parnas. “Concurrent control with ‘readers’ and ‘writers’.” *Communications of the ACM* 14(10), 667–668, October 1971. DOI: <https://doi.org/10.1145/362759.362813>.
2. Dijkstra, Edsger W. “Cooperating Sequential Processes.” In *Programming Languages*, edited by F. Genuys, Academic Press, 1968. Archival transcription of EWD 123: <https://www.cs.utexas.edu/~EWD/transcriptions/EWD01xx/EWD123.html>.
3. Hoare, C. A. R. “Monitors: an operating system structuring concept.” *Communications of the ACM* 17(10), 549–557, October 1974. DOI: <https://doi.org/10.1145/355620.361161>.
4. Peterson, Gary L. “Myths about the mutual exclusion problem.” *Information Processing Letters* 12(3), 115–116, June 1981. DOI: <https://doi.org/10.1016/0020-0190(81)90106-X>.
5. Kawash, Jalal. “Process Synchronization with Readers and Writers Revisited.” *Journal of Computing and Information Technology* 13(1), 43–51, 2005. DOI: <https://doi.org/10.2498/cit.2005.01.04>. Accessible article copy: <https://hrcak.srce.hr/file/69328>.
6. Ridge, Tom. “Operational Reasoning for Concurrent Caml Programs and Weak Memory Models.” In *Theorem Proving in Higher Order Logics (TPHOLs 2007)*, Lecture Notes in Computer Science 4732, 278–293. DOI: <https://doi.org/10.1007/978-3-540-74591-4_21>.
7. Python Software Foundation. “`threading` — Thread-based parallelism.” Python Standard Library documentation. <https://docs.python.org/3/library/threading.html>.

The repository's tests exercise one Python monitor implementation; they are not a formal proof of all algorithms or all schedules. No Python lock-fairness property is inferred from the language documentation.
