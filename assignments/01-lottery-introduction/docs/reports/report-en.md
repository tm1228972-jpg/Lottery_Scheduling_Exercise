# Exercise 1 — Lottery Scheduling: Technical Report (Short Research Draft)

> **Status:** This evidence-based working draft is shorter than the requested approximately 40-page final report. It is not padded with repeated prose. Online source metadata and the claims cited below were checked on 2026-11-23; see [the source-audit notes](../../../../docs/research-source-audit.md). The generated Word/PDF files are provisional exports of this Markdown.

## Abstract

Lottery Scheduling is a randomized proportional-share resource-allocation mechanism. A ready client receives a positive number of tickets; one uniformly drawn ticket determines the next allocation. If client `i` owns `tᵢ` tickets in an active pool of `T`, then `pᵢ=tᵢ/T` is its probability of winning one draw. With a fixed ready set and independent draws, the number of wins in `n` opportunities is binomial, with expected count `npᵢ` and variance `npᵢ(1-pᵢ)`. These statements describe expectation and dispersion, not an exact finite-trace share or a deadline guarantee. Waldspurger and Weihl introduce the mechanism and discuss extensions such as ticket transfer, inflation, currencies, and compensation tickets [1, Secs. 2–4]. This report distinguishes those published mechanisms from the smaller fixed-ticket teaching simulator in this repository and interprets one seeded 50,000-draw output without treating it as a benchmark.

## 1. Scheduling objective and system model

A scheduler chooses which ready computation receives a resource next. Different policies encode different contracts. Proportional-share scheduling answers “what long-run fraction should this client receive when it competes?” A hard real-time policy answers “will each released job finish by its deadline?” A priority scheduler says which task should preempt another, but priority alone is not a statement about either proportional share or feasibility.

The model in this assignment is deliberately small. It receives a non-empty, fixed list of ready clients. Each client has a name and a fixed, positive integer ticket count. A draw returns one client; the simulator does not execute CPU instructions, update the ready set, model a blocked or newly released process, or charge dispatch overhead. The CSV experiment therefore measures counts of abstract dispatch choices, not processor time, throughput, response time, or a kernel scheduler's performance.

## 2. Ticket allocation and one-draw probability

Let `tᵢ>0` be the number of tickets assigned to client `i`, and let `T=Σᵢtᵢ` be the active pool total. The scheduler selects a uniform integer `k∈{1,…,T}`. It partitions that integer range into disjoint cumulative intervals, one per client. Since each of client `i`'s `tᵢ` tickets is one of `T` equally likely outcomes,

`P(i wins one draw) = tᵢ/T = pᵢ`.

The intervals cover every integer from 1 to `T` exactly once. Consequently every valid draw has exactly one owner, and summing the outcome probabilities gives `Σᵢpᵢ=1`. For weights `(1,2,4)`, `T=7`: P1 owns `[1,1]`, P2 `[2,3]`, and P3 `[4,7]`. The cumulative mapping is deterministic; randomness occurs only in choosing `k`.

### Pseudocode

```text
LOTTERY(ready):
    require ready is non-empty
    T ← Σ process.tickets
    k ← uniform_integer(1, T)
    cumulative ← 0
    for process in ready:
        cumulative ← cumulative + process.tickets
        if k ≤ cumulative:
            dispatch process
            return process
```

The repository implementation scans the client list, so a draw is `O(m)` for `m` ready clients. Waldspurger and Weihl describe a partial-sum tree as an alternative for large client sets, allowing a lookup in logarithmic time after maintaining the tree [1, Sec. 4.2]. That optimization is not implemented here.

## 3. Repeated draws, variance, and waiting time

Assume the ready set and ticket pool remain fixed, and the draws are independent with constant probability `pᵢ`. Let `Xᵢ` be the number of wins by client `i` in `n` draws. Then

`Xᵢ ~ Binomial(n,pᵢ)`, `E[Xᵢ]=npᵢ`, and `Var(Xᵢ)=npᵢ(1-pᵢ)`.

Thus the expected share equals the ticket ratio, but a finite trace is random. A client with few tickets can win several successive lotteries; a high-ticket client can temporarily receive fewer wins than its expected count. The relative standard deviation of the win count is `sqrt((1-pᵢ)/(npᵢ))`, so the typical relative variation decreases as more opportunities are observed, all else fixed [1, Sec. 2.2].

The first-win time for a fixed positive `p` is geometric: the chance of no win in the first `k` opportunities is `(1-p)^k`, and the expected number of opportunities up to and including the first win is `1/p` [1, Sec. 2.2]. For every finite `k`, `(1-p)^k>0`. Its limit is zero as `k→∞`, so under this ideal fixed-`p`, infinite independent-draw model the client wins eventually with probability one, but there is no deterministic finite upper bound on the wait. This careful distinction reconciles the original paper's “eventually” wording with the absence of a bounded-wait or hard-deadline guarantee.

If the ready set changes, the probability can change too; if a client is not ready, this simple model gives it no draw at all. The preceding binomial and geometric calculations must not be applied unchanged to a schedule with dependent draws, dynamic ticket transfers, or changing eligible clients.

## 4. Ticket-management mechanisms in the literature

The original paper presents more than a weighted random draw [1, Sec. 3]:

- **Ticket transfer** temporarily assigns tickets from one client to another, for example when a client blocks while an RPC server works on its behalf. The motivation is to make resource rights follow a dependency and to mitigate priority inversion.
- **Ticket inflation** lets a client create or increase tickets. Without a policy that limits who may inflate, a client could increase its share at others' expense. The paper discusses inflation as useful among mutually trusting clients, not as an unrestricted safe default.
- **Currencies** name resource rights locally inside a group and translate them into backing tickets in a more global currency. This supports hierarchical or modular allocation while containing some local changes.
- **Compensation tickets** adjust the effective weight of a client that yields before consuming its full quantum, so that allocated service better reflects the resource actually consumed.

These are design abstractions reported by Waldspurger and Weihl, not features of `LotteryScheduler`. The repository implementation stores a fixed ticket count per process for one run; it has no currency graph, transfer lifecycle, authorization policy, compensation logic, or process-blocking model.

## 5. Implementation in this repository

`Process` is an immutable record of a unique, non-empty name and a positive integer ticket count. Invalid counts, duplicate names, and empty configurations are rejected. `LotteryScheduler` owns the process list and a seeded `random.Random` instance. `draw()` returns the selected process and the drawn ticket for inspectability; `run(n)` repeats the draw and rejects invalid trace lengths. `expected_share(name)` reports the theoretical `tᵢ/T` ratio, not the observed frequency.

The fixed seed exists so students can reproduce the teaching trace. Python's `random` module provides pseudo-random number generators, not a claim of physical randomness or a cryptographic source [2]. The probability derivations above are idealized mathematical results for independent uniform outcomes; the program's seed is an engineering tool for repeatability. No security-sensitive use is intended.

## 6. Reproducible sample and interpretation

The figure generator uses the repository code with weights `(1,2,4)`, 50,000 draws, and seed `20261123`. Exact counts are in [the seeded CSV output](../../outputs/lottery-frequency.csv):

| Client | Tickets | Expected share | Wins | Observed share |
|---|---:|---:|---:|---:|
| P1 | 1 | 14.285714% | 7,243 | 14.486% |
| P2 | 2 | 28.571429% | 14,420 | 28.840% |
| P3 | 4 | 57.142857% | 28,337 | 56.674% |
| **Total** | **7** | **100%** | **50,000** | **100%** |

For a fixed Bernoulli probability, the theoretical standard error of an observed share is `sqrt(p(1-p)/n)`. Here it is approximately 0.157 percentage points for P1, 0.202 for P2, and 0.221 for P3. This places the single seeded deviations on a plausible sampling scale, but one seed is not a statistical validation study. The table is actual program output; it is not a performance benchmark, does not establish a general error bound for a PRNG, and says nothing about deadline satisfaction.

The companion figure compares observed bars to theoretical ratios. Its purpose is to make finite-sample variation visible. A claim such as “the bars are close, therefore Lottery is fair in every run” would not follow from the experiment.

## 7. Validation and reproducibility

From the repository root:

```bash
python -m pip install -e .
python examples/run_lottery_demo.py
python -m unittest discover -s tests -v
python -m pip install -e ".[docs]"
python tools/generate_figures.py
```

The tests cover input validation, ticket interval mapping, expected share, reproducibility for equal seeds, and a seeded frequency sanity check. A finite test cannot prove a universal probability theorem; the mathematical derivation and program tests serve different purposes. The CSV records the seed, draw count, weights, and observed counts so that the chart can be regenerated and audited.

## 8. Strengths, limitations, and appropriate use

Lottery Scheduling offers an intuitive way to express relative resource claims and can react to changes in ticket allocations on the next lottery. The 1994 paper demonstrates ticket abstractions for several resource-management settings and reports a Mach 3.0 prototype; those findings are historical evidence for the proposed design, not a modern comparison with current operating systems [1].

A randomized share policy is appropriate when proportional service is the contract and variation is acceptable. It is not, by itself, an algorithm for hard deadlines, fixed worst-case latency, or deterministic bounded waiting. Its practical behavior depends on ticket policy, the ready-set model, draw frequency, run-queue implementation, overhead, and interactions with blocking. Workload changes, lock contention, multi-core scheduling, real-time release jitter, and context-switch costs need separate analysis.

## 9. Conclusion

For a fixed ready set, the ticket ratio determines a process's probability on one independent draw and its expected fraction of repeated wins. Finite traces vary; a positive ticket gives probability-one eventual selection only in the ideal infinite repeated-draw model and does not bound a finite wait. The code and CSV demonstrate a specific seeded sample. They do not implement the advanced ticket-management abstractions from the paper or measure real CPU service.

## References

1. Waldspurger, Carl A., and William E. Weihl. “Lottery Scheduling: Flexible Proportional-Share Resource Management.” *Proceedings of the First Symposium on Operating Systems Design and Implementation (OSDI ’94)*, November 1994. Full-text URL is in the adjacent `references.md`.
2. Python Software Foundation. “`random` — Generate pseudo-random numbers.” Python Standard Library documentation. Full URL is in the adjacent `references.md`.

Bibliographic and source-claim audit: [evidence and claim limits](../../../../docs/research-source-audit.md).
