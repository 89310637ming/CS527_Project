# Evaluation Setting Draft

This draft is intended to help populate Section `4.1 Evaluation Setting` of the project report.

## 4.1 Evaluation Setting

We evaluated the proposed context-aware multi-factor test prioritization technique using subject projects from the `Defects4J` benchmark. To make the study feasible while still providing meaningful cross-project evidence, we selected pilot subsets from three different subject projects:

- `Lang`
- `Math`
- `Jsoup`

For each project, we used the first `10` active bugs as an initial evaluation subset. This produced a lightweight but multi-project study design that is more credible than a single-project pilot while still remaining manageable for implementation.

### Subject Projects and Bug Selection

The current evaluation includes:

- `Lang`: `10` active bugs
- `Math`: `10` active bugs
- `Jsoup`: `10` active bugs

These projects were chosen because they are all available in `Defects4J`, provide reproducible bug metadata, and use git-based revision identifiers that align well with our source-history extraction pipeline.

### Data Collected

For each selected bug, we collected:

- the buggy revision id
- the fixed revision id
- the modified source classes
- the relevant test classes
- the triggering tests
- source patch information
- source history information from the underlying project repository

The `Defects4J` metadata was used to obtain modified classes, relevant tests, and triggering tests. The corresponding project repositories were used to compute real source-history and source-structure features at the buggy revision.

### Unit of Analysis

The ideal unit of analysis for test prioritization is an individual test case. However, in the current lightweight implementation, we use test classes as the unit of analysis because `Defects4J` exposes relevant test information naturally at the class level. Each observation therefore represents a `(bug, test class)` pair.

### Prioritization Factors

The proposed method integrates three factors:

1. `FailureHistory`
2. `ChangeFrequency`
3. `Complexity`

`FailureHistory` is computed from prior appearances of triggering behavior in earlier selected bugs. `ChangeFrequency` is computed using real git file-touch counts for source classes at the buggy revision. `Complexity` is computed using source-level size information, including lines of code and method count, with a small patch-based bonus. Because exact coverage was not collected in this implementation, tests are linked to source classes using an affinity heuristic based on class-name similarity, package overlap, and triggering stack information when available.

### Baselines

We compare the proposed method against four baselines:

- `Random`
- `FailureHistory`
- `ChangeFrequency`
- `ComplexityOnly`

These baselines allow us to compare the multi-factor model both against a naive strategy and against single-factor prioritization techniques.

### Evaluation Metric

We use `APFD` as the primary evaluation metric. APFD measures how early fault-revealing tests appear in the prioritized order. Higher APFD values indicate better prioritization effectiveness.

### Experimental Procedure

For each bug instance, we:

1. construct the `(bug, test class)` dataset
2. compute all prioritization factors
3. normalize factor values within each bug
4. rank tests using each method
5. compute APFD for each prioritized order

We then aggregate APFD values within each project and across all three projects.

### Practical Rationale

This evaluation setting is intentionally lightweight. The goal is not to build a production-ready regression prioritization framework, but to create a research-credible prototype that demonstrates whether contextual source-level signals improve prioritization effectiveness. The use of three subject projects makes the evaluation substantially stronger than a single-dataset pilot, while still keeping the implementation feasible within project scope.
