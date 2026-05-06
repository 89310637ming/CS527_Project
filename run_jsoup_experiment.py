from d4j_jsoup_utils import (
    PROJECT_ROOT,
    build_bug_metadata,
    build_test_instances,
    compute_change_frequency,
    compute_complexity_proxy,
    compute_failure_history,
    compute_risk_score,
    load_pilot_bug_ids,
    normalize_within_bug,
    run_all_methods,
)


def main() -> None:
    data_dir = PROJECT_ROOT / "data"
    data_dir.mkdir(exist_ok=True)

    pilot_bug_ids = load_pilot_bug_ids()
    bug_metadata = build_bug_metadata(pilot_bug_ids)
    bug_metadata.to_csv(data_dir / "jsoup_bug_metadata.csv", index=False)

    test_instances = build_test_instances(bug_metadata)
    test_instances.to_csv(data_dir / "jsoup_test_instances.csv", index=False)

    features = compute_failure_history(test_instances)
    features = compute_change_frequency(features)
    features = compute_complexity_proxy(features)
    features = normalize_within_bug(features)
    features = compute_risk_score(features)
    features.to_csv(data_dir / "jsoup_test_instances_features.csv", index=False)

    ranked, apfd = run_all_methods(features)
    ranked.to_csv(data_dir / "jsoup_ranked_tests.csv", index=False)
    apfd.to_csv(data_dir / "jsoup_apfd_results.csv", index=False)

    summary = apfd.groupby("method", as_index=False)["apfd"].agg(["mean", "median"]).reset_index()
    print("Jsoup experiment complete")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
