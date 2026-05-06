# CS527 Project : Context-Aware Risk-Based Test Case Prioritization

This repository contains the implementation and evaluation for CS527 research project on regression test case prioritization. The goal of this project is to improve early fault detection by ranking regression tests using a context-aware, multi-factor risk model.

Instead of prioritizing tests using only one signal, such as failure history or code coverage, this project combines multiple risk indicators:

- historical test failure behavior,
- source-code change frequency,
- source-code complexity.

The intuition is that tests associated with frequently changed, complex, or historically failure-prone code should be executed earlier because they are more likely to reveal faults.

---

## Project Overview

Regression testing is important for checking whether recent code changes introduce new bugs into existing functionality. However, large regression test suites can be expensive to run completely. Test case prioritization addresses this problem by ordering tests so that fault-revealing tests are executed earlier.

This project implements a lightweight, research-oriented test case prioritization pipeline using Defects4J projects. The final evaluation compares the proposed multi-factor prioritization method against several baseline methods using APFD, a standard metric for measuring how quickly faults are detected.

---

## Benchmark and Subject Projects

The project uses Defects4J as the benchmark source.

The evaluation includes selected bug versions from multiple Java subject projects:

| Project | Description |
|---|---|
| Lang | Apache Commons Lang |
| Math | Apache Commons Math |
| Jsoup | Jsoup HTML parser |

The implementation was designed to be lightweight and notebook-friendly so that the full pipeline can be inspected and reproduced step by step.

---

## Risk Model

Each test case is assigned a normalized risk score.

```text
risk_score(test) =
    w_f * failure_history(test)
  + w_c * change_frequency(test)
  + w_x * complexity(test)
