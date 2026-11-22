# Lottery Scheduling

Lottery Scheduling is a proportional-share CPU scheduling algorithm. Each runnable process owns tickets; a uniformly random winning ticket selects the next process. If process i owns t_i tickets out of total T, its expected share is t_i/T. Steps: collect runnable tasks, sum tickets, draw an integer in [1,T], locate the cumulative ticket interval, run the winner for one quantum, then repeat. Example: ticket counts 10,20,30 produce expected shares 1/6,1/3,1/2. Strengths: flexible share control and simple conceptual model. Limits: short-run statistical variation, dependence on ticket-allocation policy, and no hard deadline guarantee. Ticket transfer temporarily lends tickets; ticket inflation changes a task's allocation and requires authorization; currencies provide hierarchical allocation.

English: Lottery Scheduling uses randomized ticket selection to provide proportional shares in expectation. It is not a hard real-time scheduler.
