# Speaker notes for the 10-slide seminar

The deck is bilingual. The notes below provide one concise delivery path; use the two article files for expanded material.

1. **Title and framing (1 min):** Ask whether the goal is fair share or deadline completion. Point out they are separate contracts.
2. **Objectives (1 min):** Describe a fixed ticket ratio as expected share, not a service deadline.
3. **Lottery algorithm (1.5 min):** Walk through the ready set, total tickets, uniform integer, cumulative interval, and dispatch.
4. **Mathematics (1.5 min):** Derive `pᵢ=tᵢ/T`, `E[X]=np`, and `Var(X)=np(1-p)` for a fixed ready set and independent draws.
5. **Ticket mechanisms (1 min):** Define transfer, inflation, and currencies conceptually; state that this repository implements none of these abstractions.
6. **EDF and RM (2 min):** EDF uses earliest absolute deadline; RM uses shortest period. State single-CPU, preemption, implicit-deadline and zero-overhead assumptions.
7. **Comparison matrix (1.5 min):** Compare objective, priority rule, ideal result, and limitation. Do not rank algorithms by a single vague “fairness” score.
8. **Actual data (1.5 min):** Show the 50,000 seeded draws; read expected and observed fractions. Explain that a single seed is a reproducible illustration, not a performance study.
9. **Limitations (1 min):** Mention dynamic ready sets, context-switch overhead, blocking, multiprocessors, hard deadlines, and bounded waiting.
10. **Takeaways and Q&A (2 min):** Ask what happens if tickets double, why short samples vary, what transfer represents, and why proportional share is not a deadline guarantee.

Total planned time: approximately 14 minutes, including the final Q&A; adapt the agenda and slide sequence to the actual course regulation before presenting.
