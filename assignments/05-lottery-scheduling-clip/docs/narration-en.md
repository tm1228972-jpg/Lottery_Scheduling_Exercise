# Suggested narration script — Exercise 5

**Target speaking time:** about 2 minutes 15 seconds at a moderate pace. The checked-in clip currently has bilingual on-screen captions but no audio.

Hello. This clip compares three scheduling policies by their objective: Lottery Scheduling, EDF, and RM. Lottery is a proportional-share mechanism; EDF and RM prioritize deadline-constrained jobs in real-time task models. They do not simply solve one identical objective in three different ways.

In Lottery Scheduling, each ready process receives tickets. If a process has `t` tickets out of a total of `T`, its probability of winning one independent draw is `t/T`. With weights one, two, and four, the expected proportions are one seventh, two sevenths, and four sevenths. These are expectations over repeated draws. A short trace need not match them exactly. Even a process with positive probability can lose repeatedly over a finite interval, so lottery alone does not guarantee a hard deadline or a deterministic waiting bound.

EDF chooses the ready job with the earliest absolute deadline. For independent, preemptive tasks on an ideal uniprocessor, with zero overhead and deadlines equal to periods, the classical utilization condition is at most one. Rate Monotonic scheduling instead assigns fixed priority: shorter periods get higher priority. The Liu–Layland utilization bound for RM is sufficient, not necessary; exceeding it alone does not prove failure.

The repository’s three-task example has execution and period pairs of one and four, one and five, and two and ten. Utilization is sixty-five percent and the hyperperiod is twenty time units. The simulator reports no missed deadlines for either EDF or RM across that interval. Their traces happen to match for this input; that does not prove general equivalence.

The takeaway is to choose according to the system contract. Lottery can be simple and tunable when proportional share matters. EDF or RM should be selected when deadlines matter, together with analysis of the assumptions and schedulability. The repository contains the code, tests, and data used for the figures.
