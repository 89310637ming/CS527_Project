# Evaluation Results Draft

This draft is written to help populate Section `4.2 Evaluation Results` of the project report.

## 4.2 Evaluation Results

We evaluated the proposed context-aware test prioritization technique on pilot subsets of three `Defects4J` subject projects: `Lang`, `Math`, and `Jsoup`. For each project, we selected the first `10` active bugs and compared five prioritization strategies: `Random`, `FailureHistory`, `ChangeFrequency`, `ComplexityOnly`, and the proposed multi-factor method `Proposed`. Effectiveness was measured using APFD, where larger values indicate that fault-revealing tests are detected earlier in the prioritized execution order.

### Overall Cross-Project Results

Table 1 summarizes the combined APFD results across all three subject projects.

| Method | Combined Mean APFD | Combined Median APFD |
| --- | ---: | ---: |
| ChangeFrequency | 0.8316 | 0.8750 |
| ComplexityOnly | 0.8275 | 0.8750 |
| Proposed | 0.8196 | 0.8750 |
| FailureHistory | 0.5771 | 0.6080 |
| Random | 0.3963 | 0.3968 |

These results show a clear separation between source-context-aware methods and traditional baselines. In particular, the proposed multi-factor method achieves a combined mean APFD of `0.8196`, which is substantially higher than the random baseline (`0.3963`) and the failure-history-only baseline (`0.5771`). This indicates that contextual source-level information helps prioritize fault-revealing tests earlier across multiple subject projects, not just within a single dataset.

Table 2 summarizes the mean APFD values separately for each project.

| Dataset | Method | Mean APFD |
| --- | --- | ---: |
| Lang | Proposed | 0.7944 |
| Math | Proposed | 0.7786 |
| Jsoup | Proposed | 0.8859 |

The proposed method performs strongly across all three projects, which suggests that the general approach is portable beyond a single codebase.

### RQ1: Does the proposed method improve fault detection effectiveness compared to traditional techniques?

Yes. Across the combined evaluation, the proposed method improves mean APFD by approximately `0.4233` over `Random` and by approximately `0.2425` over `FailureHistory`. This is a substantial difference in a regression-testing setting, because higher APFD directly means that failure-revealing tests are executed earlier.

The per-project results support this conclusion as well. In `Lang`, the proposed method reaches a mean APFD of `0.7944`, compared with `0.4326` for `Random` and `0.5347` for `FailureHistory`. In `Math`, it reaches `0.7786`, compared with `0.3880` for `Random` and `0.4904` for `FailureHistory`. In `Jsoup`, it reaches `0.8859`, compared with `0.3681` for `Random` and `0.7062` for `FailureHistory`. These results consistently show that the proposed context-aware strategy is more effective than traditional baselines.

### RQ2: How does the proposed multi-factor model compare with single-factor approaches?

The answer is mixed. The proposed method is consistently competitive and clearly better than the failure-history-only baseline, but it is not the strongest method on average. Across the combined evaluation, `ChangeFrequency` achieves the best average performance (`0.8316`), followed closely by `ComplexityOnly` (`0.8275`), while the proposed method achieves `0.8196`.

This means the current multi-factor model is strong, but not yet optimal. The present weighting scheme combines the three factors effectively enough to outperform the traditional baselines, but it does not yet surpass the strongest single source-context factor on average. Therefore, the current results support the usefulness of multi-factor prioritization, while also suggesting that additional tuning or a more advanced combination strategy may further improve performance.

### RQ3: What is the contribution of individual contextual risk factors?

The current results suggest that the strongest predictive contribution comes from source-context-aware factors rather than historical failure data alone. Both `ChangeFrequency` and `ComplexityOnly` substantially outperform `FailureHistory` across the combined evaluation. This indicates that source-level change characteristics provide strong signals about where regression faults are likely to appear.

At the same time, `ChangeFrequency` and `ComplexityOnly` remain very close in all three projects. This suggests that the two factors are still strongly correlated in the current implementation. As a result, the present study can confidently claim that contextual source-level signals are effective, but it cannot yet clearly separate the independent contribution of each individual source-level factor. A stronger ablation analysis or a broader dataset would be needed to make that distinction more precise.

### RQ4: Is the proposed technique effective across different software projects and regression testing scenarios?

The current results provide a positive initial answer. Unlike the earlier single-project pilot, the current evaluation spans three subject projects with different codebases and bug characteristics: `Lang`, `Math`, and `Jsoup`. In all three cases, the proposed method outperforms both random prioritization and failure-history-only prioritization. This suggests that the approach generalizes beyond a single project and is effective across multiple regression testing scenarios.

However, this conclusion should still be presented carefully. The evaluation currently uses only `10` bugs per project, so the project diversity is better than before, but the total study size is still limited. Expanding the number of bugs and adding an additional project would make this conclusion stronger.

### Discussion

Overall, the cross-project evaluation supports the central idea of the project: contextual source-aware prioritization improves regression test ordering. The most important evidence is the consistent improvement of the proposed method over both random and failure-history-based prioritization across all three datasets. This means the project now has stronger empirical support than a single-dataset pilot and can reasonably claim cross-project usefulness.

At the same time, the results reveal an important nuance. Although the proposed method performs well and generalizes across projects, it is not the best-performing method on average. The strongest average results currently come from `ChangeFrequency`, with `ComplexityOnly` very close behind. One likely explanation is that the current weighting scheme (`0.40`, `0.35`, `0.25`) may not fully capture the true relative importance of the factors. Another possible explanation is that `ChangeFrequency` and `Complexity` still overlap too much, so their combination does not yet add as much independent signal as expected.

This should be presented as a research insight rather than a weakness. The study already demonstrates that contextual signals are valuable and generalizable. The remaining question is how to combine those signals most effectively.

### Threats to Validity for This Result Set

- The evaluation uses only `10` bugs per project, which limits generalizability.
- The unit of analysis is a test class rather than an individual test method.
- Test-to-code association is approximated using an affinity heuristic instead of exact dynamic coverage.
- `ChangeFrequency` and `Complexity` appear strongly correlated in the current implementation.
- The weighting scheme of the proposed model was chosen heuristically rather than tuned systematically.

## Short Version for the Report

The cross-project evaluation on `Lang`, `Math`, and `Jsoup` shows that contextual source-aware prioritization is effective. Across the combined study, the proposed multi-factor method achieved a mean APFD of `0.8196`, compared with `0.3963` for random prioritization and `0.5771` for failure-history-based prioritization. These results indicate that contextual source-level signals improve fault detection effectiveness across multiple subject projects. Although the proposed method did not outperform the strongest single contextual factor on average, it consistently performed well and generalized across all three datasets, which provides meaningful support for the project’s core hypothesis.
