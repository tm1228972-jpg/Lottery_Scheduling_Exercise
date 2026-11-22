# EDF and RM for Three Tasks

Assume three independent periodic tasks, all released at t=0, preemptive uniprocessor, zero context-switch cost, deadlines equal periods:

| Task | C | T=D |
|---|---:|---:|
| P1 | 1 | 4 |
| P2 | 1 | 5 |
| P3 | 2 | 10 |

Utilization U=1/4+1/5+2/10=0.65. RM priorities: P1, then P2, then P3 because periods are 4,5,10. At t=0 both RM and EDF choose P1 (deadline 4), then P2 (deadline 5), then P3 (deadline 10), assuming no newly released job changes the earliest-deadline order. Hyperperiod=lcm(4,5,10)=20. The RM sufficient bound for n=3 is 3(2^(1/3)-1)≈0.780; 0.65 is below this bound, so the sufficient test guarantees schedulability under the stated assumptions. A final submission should include a complete Gantt chart through t=20 and label every job's absolute deadline.

English: This task set has utilization 65% and passes the three-task RM sufficient utilization test.
