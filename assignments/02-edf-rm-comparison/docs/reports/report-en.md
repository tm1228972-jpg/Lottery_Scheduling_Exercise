# Exercise 2 — Comparing Lottery Scheduling, EDF, and RM (Short Research Draft)

> **Status:** This bilingual working report is not yet the requested approximately 40-page final submission. It presents a source-checked technical comparison rather than filling pages with repeated material. The source audit is documented in [the source-audit record](../../../../docs/research-source-audit.md); the Word/PDF files are provisional exports.

## Abstract

Lottery Scheduling, Earliest Deadline First (EDF), and Rate Monotonic (RM) encode different service objectives. Lottery assigns expected proportional share through ticket counts. EDF dynamically selects a ready job with the earliest absolute deadline. RM assigns fixed task priorities according to period. A comparison that calls one policy simply “fairer” or “faster” is incomplete unless it states the workload, processor, preemption and overhead model, ticket policy, and measured property. This report separates expected share, short-run variance, response time, deadline feasibility, and starvation. It applies the classical EDF/RM utilization results only to their stated ideal uniprocessor task model and uses the repository's three-task schedule as one reproducible example [1, 2].

## 1. Questions a scheduler can answer

A proportional-share system specifies how a contested resource should be divided among active clients. A real-time system specifies job release times, execution requirements, deadlines, and a service policy intended to meet those deadlines. These contracts are related but not interchangeable:

- **Share:** what fraction of repeated allocation opportunities should a client receive?
- **Deadline feasibility:** can every job finish by its deadline under the assumed workload and scheduler?
- **Response time:** how long can a released job wait and execute before completing?
- **Fairness/starvation:** what progress is guaranteed to an individual request, under what arrivals and scheduling assumptions?

A policy may do well on one measure and poorly on another. For example, a high expected CPU share does not imply a bound on one job's completion time. Conversely, meeting deadlines for a feasible task set does not mean all tasks receive equal processor fractions.

## 2. Model and assumptions

The classical comparison uses independent periodic tasks `τᵢ=(Cᵢ,Tᵢ,Dᵢ)` on one preemptive processor. `Cᵢ` is worst-case execution demand, `Tᵢ` the period, and `Dᵢ` the relative deadline. The simple utilization model is `U=Σ(Cᵢ/Tᵢ)`. The exact conditions quoted below require an idealized model: no blocking or context-switch cost, no release jitter, no multiprocessor interference, and the stated deadline relationship. Liu and Layland's original work concerns a single processor and contrasts fixed-priority scheduling with dynamic priorities based on current deadlines [1]. Real systems may require blocking terms, response-time or demand analysis, and explicit overhead budgets.

Lottery has a different base model. For a fixed ready set, process `i` has `tᵢ` tickets from a total `T`, and independent uniform draws give it probability `pᵢ=tᵢ/T` per dispatch. If readiness or ticket ownership changes, probabilities change. The repository's simulator models integer dispatch choices, not the execution times `Cᵢ` in a real-time task model [2].

## 3. Lottery Scheduling: expected share and finite variation

For `n` independent opportunities with a fixed `pᵢ`, the number of wins `Xᵢ` is binomial:

`E[Xᵢ]=npᵢ`, `Var(Xᵢ)=npᵢ(1-pᵢ)`.

The expected fraction of draws is the ticket ratio. But a finite trace may differ; the probability of no win in `k` draws is `(1-pᵢ)^k`, and the expected first-win opportunity is `1/pᵢ` under this fixed-probability model [2, Sec. 2.2]. For any finite `k`, the no-win probability is positive. It tends to zero as `k` grows without bound, so positive tickets imply eventual selection with probability one in the ideal infinite independent process, not a deterministic finite waiting bound. A hard deadline therefore cannot be inferred from Lottery share alone.

Lottery's apparent fairness depends on the contract and the sample horizon. “Expected ticket share,” “equality of observed counts,” “bounded waiting,” and “no missed deadlines” are different claims. The original Lottery paper also discusses transfer, inflation, currency, and compensation tickets [2, Sec. 3]; these policy mechanisms can alter effective claims and require authority rules. They are not implemented by the fixed-ticket model used here.

## 4. EDF: dynamic priority by absolute deadline

EDF assigns priority dynamically: among ready jobs on a uniprocessor, the job with the smallest absolute deadline is selected. Under the classical model of independent, preemptive tasks with implicit deadlines (`Dᵢ=Tᵢ`) and zero overhead, utilization `U≤1` is the exact feasibility condition for EDF [1]. “Exact” applies to those assumptions; it does not imply that arbitrary deadline constraints, blocking, jitter, non-preemption, multicore placement, or resource contention can be ignored.

EDF's dynamic ranking is directly related to urgency. Under overload, total demand can exceed available processor capacity and deadlines can be missed. A particular overload policy may add admission control, deadline degradation, or service reservation; plain EDF does not by itself define those policies. A deadline miss is a task-level timing failure, not automatically the same thing as permanent starvation.

## 5. RM: fixed priority by period

RM assigns each periodic task a fixed priority: the shorter its period, the higher its priority. For `n` independent, preemptive, implicit-deadline tasks on an ideal uniprocessor, the Liu–Layland bound

`U ≤ n(2^(1/n) − 1)`

gives a sufficient schedulability test [1]. It is not a necessary condition. A task set above the bound may still be schedulable; failure of the sufficient test means “inconclusive,” not “unschedulable.” For a specific fixed-priority task set, worst-case response-time analysis can give a more precise test under its own assumptions [3]. High-priority interference can lengthen lower-priority response times; resource blocking and priority inversion require additional treatment.

## 6. Comparison by property

| Property | Lottery | EDF | RM |
|---|---|---|---|
| Primary contract | Expected proportional allocation | Deadline feasibility | Fixed-priority periodic service |
| Selection key | Random ticket among eligible clients | Earliest absolute deadline | Shorter task period; fixed priority |
| Priority type | Probabilistic/weighted | Dynamic per ready job | Static per task |
| Ideal result | `pᵢ=tᵢ/T`; binomial count over fixed independent draws | `U≤1` is exact for independent preemptive implicit-deadline uniprocessor tasks | `n(2^(1/n)−1)` is sufficient, not necessary, under the classical model |
| Finite wait | No deterministic finite bound from the draw rule alone | Feasible jobs meet deadlines under assumptions | Feasible tasks meet deadlines under assumptions; low priority sees higher-priority interference |
| Overload concern | Share remains probabilistic; real-time feasibility is not provided | Capacity may be exceeded and deadlines missed | Low-priority response may grow; utilization bound alone may be inconclusive |
| Needs explicit policy for | Ticket creation, transfer, dynamic ready set | Overload handling, resource blocking, tie-breaking | Admission test, blocking/priority-inversion handling |
| Repository model | Fixed tickets, seeded discrete draws | Integer-tick preemptive trace | Integer-tick fixed-priority trace |

“Fairness” is not one row that can substitute for every result. It should be operationalized (for example, probability share, maximum bypass count, maximum response time, or deadline-miss ratio) before algorithms are ranked.

## 7. Starvation and waiting-time distinctions

Three cases illustrate the distinction:

1. **Lottery:** with fixed positive `p`, `P(no win after k)=(1-p)^k`. A long finite delay is possible, though its probability decreases with `k`. The process wins eventually with probability one in the ideal infinite sequence, but the scheduler gives no deterministic bound for an individual finite wait [2].
2. **RM:** if a task set is schedulable under the assumed model, each periodic job meets its deadline; calling a low-priority task “starved” in that case is incorrect. In an overloaded or otherwise infeasible workload, high-priority demand can repeatedly delay or cause misses for a lower-priority task. Exact behavior depends on releases, execution, blocking, and deadlines.
3. **EDF:** when the task set is feasible, the ideal theorem provides deadline satisfaction. Under overload, misses can occur. A missed deadline does not by itself prove that a job was permanently denied CPU; starvation needs a separate definition and trace.

For synchronization, the same discipline applies: reader/writer starvation depends on arrival and admission policy. A reader-preference solution can let continuing readers defer writers; a writer-preference solution can defer readers. A FIFO queue or fair admission mechanism can change those bounds, at a possible cost to batching or throughput. No general fairness property follows from the label “priority” alone.

## 8. Worked repository example

Exercise 3 retains the task set found in the original assignment branch:

| Task | `Cᵢ` | `Tᵢ` | `Dᵢ` |
|---|---:|---:|---:|
| P1 | 1 | 4 | 4 |
| P2 | 1 | 5 | 5 |
| P3 | 2 | 10 | 10 |

`U=1/4+1/5+2/10=0.65` and the hyperperiod is `H=lcm(4,5,10)=20`. The three-task RM sufficient bound is `3(2^(1/3)-1)≈0.779763`; thus this task set passes that sufficient test. EDF also passes the implicit-deadline `U≤1` test. The hand-calculated trace and the simulator both show no deadline miss in `[0,20)`. The traces happen to match for this input only. No ticket counts were supplied for these tasks, so a Lottery share for this workload is deliberately not invented.

## 9. Method, implementation, and limitations

The two figures in this assignment explain policy goals and guarantee boundaries; they are conceptual comparisons, not benchmark plots. The Gantt figure and CSV in Exercise 3 are generated from `src/lottery_lab/realtime.py` using the task set above. The simulator dispatches in integer ticks, allows preemption at tick boundaries, assumes one processor and zero overhead, and uses deterministic tie-breaking. It does not model WCET uncertainty, blocking, release jitter, context-switch cost, or multicore scheduling. Tests establish behavior for listed cases, not a theorem for arbitrary task sets.

Reproduce the current local artifacts with:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python tools/generate_figures.py
```

## 10. Conclusion

Select a scheduler from the service contract and then validate its assumptions. Lottery is a proportional-share mechanism; a positive expected share is not a hard deadline guarantee. EDF has a strong exact result for the ideal implicit-deadline uniprocessor model. RM is fixed-priority and offers a simple sufficient utilization bound plus more detailed task-specific analyses. Starvation, utilization, deadline misses, and average share must remain separate metrics.

## References

1. Liu, C. L., and James W. Layland. “Scheduling Algorithms for Multiprogramming in a Hard-Real-Time Environment.” *Journal of the ACM* 20(1), 46–61, January 1973. DOI: 10.1145/321738.321743.
2. Waldspurger, Carl A., and William E. Weihl. “Lottery Scheduling: Flexible Proportional-Share Resource Management.” *Proceedings of OSDI ’94*, November 1994. Full-text URL is in `references.md`.
3. Joseph, Mathai, and Paritosh Pandya. “Finding response times in a real-time system.” *The Computer Journal* 29(5), 390–395, 1986. DOI: 10.1093/comjnl/29.5.390.

Source-check notes: [the source-audit record](../../../../docs/research-source-audit.md).
