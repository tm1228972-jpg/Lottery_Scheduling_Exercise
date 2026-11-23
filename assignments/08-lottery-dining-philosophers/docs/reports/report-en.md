# Technical Note — Exercise 8: Lottery Scheduling and Dining Philosophers

**Document type:** concise code-backed technical note, not the requested 35–40-page final report
**Figure trace configuration:** five philosophers; ticket weights 1–5; seed `20261123`; age threshold 3

## Abstract

This note asks whether Lottery Scheduling can prevent deadlock and starvation in the dining-philosophers problem. Lottery selection alone guarantees neither: CPU dispatch and resource allocation are separate concerns. A central arbiter that atomically reserves both forks prevents deadlock in the stated model. An age override that admits the oldest request after a threshold bounds waiting under the model's finite-round assumptions. These properties come from the added allocation and fairness policies, not from random selection itself.

## 1. Problem distinction

A scheduler chooses which process receives execution time. Dining philosophers additionally requires exclusive ownership and an acquisition protocol for forks. If each philosopher holds one fork and waits for the next, selecting one of those blocked processes again does not free a fork; lottery selection alone does not break the circular wait.

Starvation is different from deadlock: the system may continue making progress while one request is repeatedly bypassed. If a request remains eligible for independent draws with constant probability `p`, the probability of not winning `k` opportunities is `(1-p)^k`. For finite `k`, this is not zero, so lottery alone gives no deterministic finite waiting bound.

## 2. Combined algorithm

At the start of each round, all forks are free and all philosophers are hungry. If the optional wait-age threshold has been reached, the arbiter admits the oldest qualified request first. It then uses weighted lottery among candidates that do not share forks with already admitted philosophers. Each grant atomically reserves both neighboring forks. Meals finish at the end of the round and both forks are released.

### Pseudocode

```text
for each round:
    eaters ← empty set
    if an aged request exists:
        p ← oldest aged request
        atomically reserve both adjacent forks; add p to eaters
    while a safe candidate exists:
        p ← weighted lottery among safe candidates
        atomically reserve both adjacent forks; add p to eaters
    finish every finite meal; release both forks
    reset ages of served philosophers; increment all other ages
```

A real concurrent implementation must protect check-and-grant in a critical section or equivalent atomic primitive. Running this sequence without synchronization would permit races.

## 3. Safety and liveness reasoning

**Deadlock safety in the model:** no philosopher holds one fork while waiting for a second. A grant is an atomic pair, which removes hold-and-wait from the modeled admission path. Finite meals are required so every reservation is eventually released.

**Lottery-only progress:** a positive ticket count provides a nonzero chance per eligible draw, not a finite bound. Under fixed candidates and independent constant-probability draws, the no-win probability after `k` opportunities is `(1-p)^k`. Resource-aware candidate sets change over time, so this formula applies only under the stated fixed-set assumption.

**Age-override progress:** after `K` rounds of waiting, the request is promoted deterministically. Since all forks are free at the start of a round, the oldest qualified request is immediately eligible for the first grant. With a finite number of philosophers and finite meals, aged requests are served in turn. A real-time bound would also need to include meal durations and arrivals/departures.

## 4. Policy comparison

| Policy | Deadlock | Starvation | Reason |
|---|---|---|---|
| Lottery without a resource protocol | Possible | No deterministic guarantee | Dispatcher does not define fork ownership |
| Atomic arbiter + lottery among safe candidates | Excluded in this model | No deterministic guarantee | Partial holding is removed, but selection remains random |
| Atomic arbiter + oldest-first threshold | Excluded in this model | Bounded under model assumptions | The deterministic guard supplies fairness; lottery does not |

Global resource ordering and a butler are other standard approaches; they are not implemented in this package.

## 5. Implementation and reproducible run

`DiningPhilosophers` stores wait ages, ticket weights, seed, and meal counts. `_adjacent()` detects shared forks; `_weighted_choice()` chooses only among currently safe candidates. `PhilosopherRound` records each round and its updated ages. A runtime invariant rejects any round containing adjacent eaters.

The figure generator uses `N=5`, tickets `[1,2,3,4,5]`, seed `20261123`, threshold 3, and 20 rounds. The full event trace is `outputs/philosopher-rounds.csv`. The 12-round example prints meal counts `(4,5,4,5,6)`. These are outcomes of this specific seeded teaching model, not real-time measurements or threaded OS results.

## 6. Figure interpretation

- `figures/atomic-fork-admission.svg` shows the central arbiter and pairwise grant/release; atomicity is the modeled reason partial holding cannot occur.
- `figures/lottery-aging-flow.svg` shows the deterministic threshold path and ordinary weighted-lottery path.
- `figures/philosopher-gantt.png` uses columns for rounds and rows for philosophers. Teal indicates lottery admission; coral indicates age override. Adjacent cells in a column must not both be filled.

## 7. Limitations and conclusion

A central arbiter may be a bottleneck. The simulator is discrete-round and circular; every meal has finite one-round duration; continuous arrivals, cancellation, timeouts, actual OS scheduling, races, and real elapsed time are not modeled. The defensible conclusion is that lottery can be one selection policy among eligible requests, but deadlock prevention requires an allocation protocol and starvation freedom requires an explicit fairness mechanism plus liveness assumptions.

## 8. Reproduction, files, and reference

```bash
python -m pip install -e .
python examples/run_philosophers_demo.py
python -m unittest discover -s tests -v
python -m pip install -e ".[docs]"
python tools/generate_figures.py
```

Code: `src/lottery_lab/philosophers.py`; tests: `tests/test_philosophers.py`; trace: `outputs/philosopher-rounds.csv`; figures: `figures/`; detailed guide: `docs/README.md`.

No original code or reports were present in the seed checkout. This is a concise note, and no 35–40-page DOCX/PDF was generated. A full report needs instructor-approved sources and formatting requirements. Suggested classic background reading, to verify against the instructor's citation style: E. W. Dijkstra, “Cooperating Sequential Processes” (1965). This note does not claim that the simulation is a production concurrent solution.
