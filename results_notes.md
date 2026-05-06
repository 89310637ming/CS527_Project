# Results Notes

This note summarizes the current `Lang` pilot results from `data/lang_apfd_results.csv`.

## Average APFD by Method

| Method | Mean APFD | Median APFD |
| --- | ---: | ---: |
| ChangeFrequency | 0.8069 | 0.8750 |
| ComplexityOnly | 0.8069 | 0.8750 |
| Proposed | 0.7944 | 0.8750 |
| FailureHistory | 0.5347 | 0.5625 |
| Random | 0.4326 | 0.4444 |

## Improvement over Random

| Method | Mean APFD Gain over Random |
| --- | ---: |
| ChangeFrequency | 0.3743 |
| ComplexityOnly | 0.3743 |
| Proposed | 0.3618 |
| FailureHistory | 0.1021 |

## Main Observations

1. All context-aware source-risk methods outperform the random baseline on average in the current `Lang` pilot.
2. The proposed multi-factor method also clearly outperforms the failure-history-only baseline on average.
3. The proposed method is best or tied for best on most pilot bugs, including bugs `1`, `3`, `4`, `5`, `6`, `7`, `8`, `10`, and `11`.
4. On bug `9`, the `ChangeFrequency` and `ComplexityOnly` methods slightly outperform the proposed method.
5. The `ChangeFrequency` and `ComplexityOnly` methods are identical in the current pilot, suggesting that the two non-history factors are still highly correlated for this subset of `Lang`.

## Report-Ready Interpretation

The pilot results suggest that adding contextual source-level risk information improves regression test prioritization effectiveness over both random ordering and failure-history-only prioritization. In particular, the proposed method achieves a mean APFD of `0.7944`, which is substantially higher than the random baseline (`0.4326`) and the failure-history-only baseline (`0.5347`). These results indicate that contextual signals derived from the modified source code can help rank fault-revealing tests earlier in the execution order.

At the same time, the current pilot also shows that the `ChangeFrequency` and `ComplexityOnly` methods behave very similarly. This suggests that, for the selected `Lang` bugs, the two source-level factors overlap strongly and do not yet provide clearly separable contributions. Therefore, the current pilot supports the overall value of contextual risk signals, but it also highlights the need for further analysis when interpreting the individual contribution of each factor.

## Limitations to Mention

- The pilot uses only a small subset of `Lang` bugs.
- The unit of analysis is a test class rather than a single test method.
- Test-to-code association is approximated with an affinity heuristic rather than exact coverage.
- The change-frequency and complexity signals are still highly correlated in this pilot.

## Suggested Next Steps

1. Expand the evaluation to more `Lang` bugs.
2. Add an ablation section that removes one factor at a time.
3. If time allows, repeat the same pipeline on `Chart`.
