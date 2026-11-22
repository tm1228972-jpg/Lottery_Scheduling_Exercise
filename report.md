# EDF and RM Comparison

Rate Monotonic (RM) assigns fixed priorities: shorter-period tasks get higher priority. Earliest Deadline First (EDF) dynamically selects the ready job with the earliest absolute deadline. For periodic tasks with execution C_i and period T_i, utilization is U=sum(C_i/T_i). Under the classical independent, preemptive, uniprocessor model with deadlines equal to periods, EDF is schedulable when U≤1. The Liu–Layland sufficient RM bound is U≤n(2^(1/n)-1), approaching ln(2)≈0.693. Exceeding this bound does not prove unschedulability; it only means the sufficient test cannot guarantee it. RM offers fixed priorities and simpler analysis; EDF has higher theoretical utilization in the ideal model but requires dynamic deadline management.

English: RM is fixed-priority and period-based; EDF is dynamic and deadline-based.
