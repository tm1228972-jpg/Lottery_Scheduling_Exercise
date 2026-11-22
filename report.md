# Lottery Scheduling Seminar

Abstract: Lottery Scheduling is a proportional-share resource management method. Tickets encode relative claims on CPU time, and a random draw selects the next runnable task. Its abstractions include ticket transfer, ticket inflation, and currencies for hierarchical allocation. The key theoretical distinction is between expected long-run share and guaranteed short-term service. Advantages include flexibility, simple weighted allocation, and extensibility to shared resources. Limitations include statistical variance, dependence on ticket-allocation policy, and lack of hard deadline guarantees. Evaluation should compare observed shares with theoretical shares across multiple ticket ratios and many draws, report sample size and random seeds, and avoid claiming exact equality for finite samples.

Seminar questions: (1) What happens to a task's expected share when its tickets double? (2) Why can a short run differ from the expected ratio? (3) What problem can ticket transfer address? (4) Why does proportional share not guarantee a hard deadline?

English: Lottery Scheduling is useful when flexible proportional allocation matters more than deterministic per-job deadlines.
