# Multi-Project Results Notes

This note summarizes the current cross-project evaluation using the `Lang`, `Math`, and `Jsoup` subject projects from `Defects4J`.

## Datasets Included

- `Lang`: first `10` active bugs
- `Math`: first `10` active bugs
- `Jsoup`: first `10` active bugs

## Mean APFD by Dataset and Method

| Dataset | Method | Mean APFD | Median APFD |
| --- | --- | ---: | ---: |
| Lang | ChangeFrequency | 0.8069 | 0.8750 |
| Lang | ComplexityOnly | 0.8069 | 0.8750 |
| Lang | Proposed | 0.7944 | 0.8750 |
| Lang | FailureHistory | 0.5347 | 0.5625 |
| Lang | Random | 0.4326 | 0.4444 |
| Math | ChangeFrequency | 0.8020 | 0.8185 |
| Math | ComplexityOnly | 0.7980 | 0.8185 |
| Math | Proposed | 0.7786 | 0.7560 |
| Math | FailureHistory | 0.4904 | 0.5417 |
| Math | Random | 0.3880 | 0.3521 |
| Jsoup | ChangeFrequency | 0.8859 | 0.9523 |
| Jsoup | ComplexityOnly | 0.8775 | 0.9523 |
| Jsoup | Proposed | 0.8859 | 0.9523 |
| Jsoup | FailureHistory | 0.7062 | 0.7612 |
| Jsoup | Random | 0.3681 | 0.3674 |

## Combined Mean APFD Across Both Projects

| Method | Combined Mean APFD | Combined Median APFD |
| --- | ---: | ---: |
| ChangeFrequency | 0.8316 | 0.8750 |
| ComplexityOnly | 0.8275 | 0.8750 |
| Proposed | 0.8196 | 0.8750 |
| FailureHistory | 0.5771 | 0.6080 |
| Random | 0.3963 | 0.3968 |

## Main Cross-Project Observations

1. The source-context-aware methods consistently outperform `Random` across `Lang`, `Math`, and `Jsoup`.
2. The proposed multi-factor method also consistently outperforms `FailureHistory` across all three projects.
3. The overall ordering of the methods is similar across all datasets, which suggests the approach generalizes beyond a single project.
4. `ChangeFrequency` and `ComplexityOnly` remain very close in all three projects, which suggests that these two factors are still strongly correlated in the current implementation.
5. The proposed method is competitive across all three projects, but it is not yet the best method on average.

## Report-Ready Interpretation

The cross-project results strengthen the main claim of the project. When evaluated on pilot subsets of `Lang`, `Math`, and `Jsoup`, the context-aware prioritization strategies consistently outperform random prioritization and failure-history-only prioritization. In the combined analysis, the proposed method achieves a mean APFD of `0.8196`, compared with `0.3963` for random prioritization and `0.5771` for failure-history-based prioritization. This shows that contextual source-level signals are useful across multiple subject projects, which improves the credibility of the study beyond a single-dataset evaluation.

At the same time, the results also show that the current proposed combination is not yet stronger than the best single contextual factor on average. This means the project should present the current method as a strong and generalizable contextual baseline, while also acknowledging that the final factor weighting and interaction strategy still need refinement.

## Suggested Next Steps

1. Expand the number of bugs in `Lang`, `Math`, and `Jsoup`.
2. Add ablation experiments to isolate each factor more clearly.
3. Add a fourth project, such as `Chart`, if time permits.
