# Lang Pilot Methodology

This document defines a practical methodology for the `Defects4J Lang` pilot.

## Goal

Evaluate whether a simple multi-factor risk score prioritizes regression tests better than lightweight baselines for `Lang` bugs in `Defects4J`.

## Unit of Analysis

The ideal unit of analysis is a test case within a bug instance.

For the lightweight pilot implementation, we approximate this with a test class within a bug instance because `Defects4J` provides `relevant_tests` at the class level.

Each observation should be represented like this:

- `project_id`
- `bug_id`
- `test_id`
- `is_triggering`
- `failure_history_raw`
- `change_frequency_raw`
- `complexity_raw`
- `failure_history_norm`
- `change_frequency_norm`
- `complexity_norm`
- `risk_score`
- `rank_random`
- `rank_failure_history`
- `rank_change_frequency`
- `rank_proposed`

## Data Table Design

Use one main table called `test_instances`.

Each row represents one test case for one bug instance.

Suggested columns:

| column | description |
| --- | --- |
| `project_id` | `Lang` |
| `bug_id` | Defects4J bug id |
| `test_id` | fully qualified test name |
| `is_triggering` | `1` if the test triggers the bug, else `0` |
| `associated_class_count` | number of linked modified classes |
| `failure_history_raw` | prior empirical failure rate |
| `change_frequency_raw` | average commit count or churn over linked classes |
| `complexity_raw` | average complexity proxy over linked classes |
| `failure_history_norm` | min-max normalized within bug |
| `change_frequency_norm` | min-max normalized within bug |
| `complexity_norm` | min-max normalized within bug |
| `risk_score` | weighted final score |

## Factor Computation Details

### Failure History

For bug `b` and test `t`:

`failure_history_raw(t, b) = failures_before_b(t) / executions_before_b(t)`

Implementation note:

- Sort pilot bugs by bug id
- For each bug, compute history using only earlier bugs in the selected sample
- If a test never appears before, assign `0`

This is simple, reproducible, and enough for a lightweight prototype.

### Change Frequency

For each modified class associated with a bug:

- count commits touching that class before the fixed revision
- optionally use file-level churn instead of commit count

For test `t`:

`change_frequency_raw(t, b) = mean(change_count(class))`

Current implementation:

- use real git history from the local `commons-lang` repository
- compute affinity-weighted file-touch counts at the buggy revision

### Complexity

Use the simplest metric that is easy to automate consistently.

Priority order:

1. cyclomatic complexity
2. method count
3. lines of code
4. changed lines

For the first deliverable, using `lines of code` or `method count` is acceptable if cyclomatic complexity setup is not smooth.

Current implementation:

- use source metrics from the buggy revision in `commons-lang`
- compute a simple complexity proxy from lines of code and method count
- add a small patch-hunk bonus

## Normalization

Within each bug instance, normalize each raw factor into `[0, 1]` using min-max normalization:

`norm(x) = (x - min(x)) / (max(x) - min(x))`

If `max(x) = min(x)`, set normalized value to `0`.

This keeps the model easy to explain and avoids scale mismatch.

## Final Score

Default score:

`risk_score = 0.40 * failure_history_norm + 0.35 * change_frequency_norm + 0.25 * complexity_norm`

Sensitivity option:

- also run equal weights as a robustness check

## Prioritization Procedures

For every bug instance:

1. collect all candidate tests
2. compute baseline scores and proposed score
3. sort descending by score
4. break ties randomly but record the random seed
5. evaluate fault detection order

## APFD

For a prioritized test order of length `n` with `m` fault-revealing tests:

`APFD = 1 - (sum(TF_i) / (n * m)) + (1 / (2 * n))`

Where `TF_i` is the position of the `i`th fault-revealing test.

Implementation note:

- for the pilot, treat the triggering tests provided by Defects4J as the fault-revealing tests

## Minimum Viable Experiment

To keep this feasible:

- start with `10` Lang bugs
- compute all methods on the same test sets
- report mean APFD and per-bug APFD
- include one ablation table

## Suggested Result Tables

Table 1:

- number of bugs
- number of tests
- average tests per bug
- average modified classes per bug

Table 2:

- mean APFD for Random
- mean APFD for FailureHistory
- mean APFD for ChangeFrequency
- mean APFD for Proposed

Table 3:

- Proposed full model
- Proposed without failure history
- Proposed without change frequency
- Proposed without complexity

## Threats to Validity

Be explicit about these in the report:

- test-to-code association is coarse without full coverage
- failure history is approximated from available bug ordering
- complexity may use a proxy instead of exact cyclomatic complexity
- pilot uses only a subset of Defects4J projects

## Expansion Path

Once `Lang` is working:

1. repeat on `Chart`
2. compare whether improvements remain consistent
3. add coverage only if the setup cost is low
