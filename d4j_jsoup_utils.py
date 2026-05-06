from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import re
import subprocess
from difflib import SequenceMatcher
from typing import Dict, Iterable, List

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent
D4J_ROOT = PROJECT_ROOT / "defects4j"
JSOUP_ROOT = D4J_ROOT / "framework" / "projects" / "Jsoup"
JSOUP_REPO = PROJECT_ROOT / "project_repos" / "jsoup"


@dataclass(frozen=True)
class PatchStats:
    added: int = 0
    deleted: int = 0
    hunks: int = 0

    @property
    def changed(self) -> int:
        return self.added + self.deleted


@dataclass(frozen=True)
class SourceMetrics:
    loc: int = 0
    method_count: int = 0

    @property
    def score(self) -> float:
        return float(self.loc + (5 * self.method_count))


def read_nonempty_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def class_name_from_source_path(source_path: str) -> str:
    if "src/main/java/" not in source_path:
        return source_path
    relative = source_path.split("src/main/java/", 1)[1]
    if relative.endswith(".java"):
        relative = relative[:-5]
    return relative.replace("/", ".")


def source_path_from_class_name(class_name: str) -> str:
    return "src/main/java/" + class_name.replace(".", "/") + ".java"


def parse_active_bugs() -> pd.DataFrame:
    path = JSOUP_ROOT / "active-bugs.csv"
    return pd.read_csv(path)


def default_pilot_bug_ids(limit: int = 10) -> List[int]:
    active = parse_active_bugs()
    return active["bug.id"].head(limit).astype(int).tolist()


def load_pilot_bug_ids() -> List[int]:
    selection_path = PROJECT_ROOT / "jsoup_bug_selection.csv"
    if not selection_path.exists():
        return default_pilot_bug_ids()

    selection = pd.read_csv(selection_path)
    selected = selection.loc[
        selection["selected_for_pilot"].astype(str).str.lower() == "yes",
        "bug_id",
    ].astype(int)
    active_ids = set(parse_active_bugs()["bug.id"].astype(int))
    return [bug_id for bug_id in selected.tolist() if bug_id in active_ids]


def parse_trigger_file(path: Path) -> List[str]:
    tests: List[str] = []
    for line in read_nonempty_lines(path):
        if line.startswith("--- "):
            tests.append(line[4:].strip())
    return tests


def parse_trigger_stack_classes(path: Path) -> List[str]:
    classes = []
    pattern = re.compile(r"\bat ([A-Za-z0-9_$.]+)\.[A-Za-z0-9_$<>]+\(.*\)")
    for line in read_nonempty_lines(path):
        match = pattern.search(line)
        if not match:
            continue
        class_name = match.group(1)
        if class_name.startswith("org.jsoup"):
            classes.append(class_name)
    return sorted(set(classes))


def trigger_classes(trigger_tests: Iterable[str]) -> List[str]:
    classes = []
    for test_id in trigger_tests:
        classes.append(test_id.split("::", 1)[0])
    return sorted(set(classes))


def parse_src_patch_stats(bug_id: int) -> Dict[str, PatchStats]:
    patch_path = JSOUP_ROOT / "patches" / f"{bug_id}.src.patch"
    stats: Dict[str, PatchStats] = {}
    if not patch_path.exists():
        return stats

    current_class = None
    added = 0
    deleted = 0
    hunks = 0

    def flush_current() -> None:
        nonlocal current_class, added, deleted, hunks
        if current_class is not None:
            stats[current_class] = PatchStats(added=added, deleted=deleted, hunks=hunks)
        current_class = None
        added = 0
        deleted = 0
        hunks = 0

    for raw_line in patch_path.read_text().splitlines():
        if raw_line.startswith("diff --git "):
            flush_current()
            continue
        if raw_line.startswith("+++ b/"):
            current_class = class_name_from_source_path(raw_line[6:])
            continue
        if raw_line.startswith("@@"):
            hunks += 1
            continue
        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            added += 1
            continue
        if raw_line.startswith("-") and not raw_line.startswith("---"):
            deleted += 1

    flush_current()
    return stats


def parse_modified_classes(bug_id: int) -> List[str]:
    path = JSOUP_ROOT / "modified_classes" / f"{bug_id}.src"
    return read_nonempty_lines(path)


@lru_cache(maxsize=None)
def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(JSOUP_REPO), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


@lru_cache(maxsize=None)
def git_commit_touch_count(revision: str, class_name: str) -> int:
    source_path = source_path_from_class_name(class_name)
    output = git_output("rev-list", "--count", revision, "--", source_path).strip()
    return int(output) if output else 0


def strip_java_comments(source: str) -> str:
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    source = re.sub(r"//.*", "", source)
    return source


@lru_cache(maxsize=None)
def git_source_metrics(revision: str, class_name: str) -> SourceMetrics:
    source_path = source_path_from_class_name(class_name)
    try:
        source = git_output("show", f"{revision}:{source_path}")
    except subprocess.CalledProcessError:
        return SourceMetrics()

    cleaned = strip_java_comments(source)
    loc = sum(1 for line in cleaned.splitlines() if line.strip())
    method_pattern = re.compile(
        r"\b(public|protected|private)\s+(static\s+)?([\w<>\[\],.?]+\s+)+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        re.M,
    )
    method_count = len(method_pattern.findall(cleaned))
    return SourceMetrics(loc=loc, method_count=method_count)


def package_tail(name: str) -> List[str]:
    parts = name.split(".")
    if len(parts) < 2:
        return []
    package_parts = parts[:-1]
    base = ["org", "jsoup"]
    if package_parts[: len(base)] == base:
        package_parts = package_parts[len(base) :]
    return package_parts


def normalize_test_name(test_id: str) -> str:
    simple_name = test_id.split(".")[-1]
    simple_name = re.sub(r"(Test|Tests|TestCase)$", "", simple_name)
    return simple_name.lower()


def simple_class_name(class_name: str) -> str:
    return class_name.split(".")[-1].lower()


def class_affinity_scores(test_id: str, modified_classes: List[str]) -> Dict[str, float]:
    normalized_test = normalize_test_name(test_id)
    test_package = package_tail(test_id)
    scores: Dict[str, float] = {}

    if not modified_classes:
        return scores

    if len(modified_classes) == 1:
        only_class = modified_classes[0]
        simple_name = simple_class_name(only_class)
        ratio = SequenceMatcher(None, normalized_test, simple_name).ratio()
        baseline = 0.25
        if normalized_test == simple_name:
            baseline = 1.0
        elif normalized_test in simple_name or simple_name in normalized_test:
            baseline = 0.85
        elif ratio >= 0.6:
            baseline = max(baseline, round(ratio, 4))
        scores[only_class] = baseline
        return scores

    exact_matches = []
    fuzzy_matches = {}

    for class_name in modified_classes:
        simple_name = simple_class_name(class_name)
        class_package = package_tail(class_name)
        score = 0.0

        if normalized_test == simple_name:
            score = 1.0
            exact_matches.append(class_name)
        elif normalized_test in simple_name or simple_name in normalized_test:
            score = 0.85
        else:
            ratio = SequenceMatcher(None, normalized_test, simple_name).ratio()
            if ratio >= 0.6:
                score = max(score, round(ratio, 4))

        if test_package and class_package:
            overlap = len(set(test_package) & set(class_package))
            if overlap:
                score += min(0.25, 0.1 * overlap)

        score = min(score, 1.0)
        if score > 0:
            fuzzy_matches[class_name] = score

    if exact_matches:
        return {class_name: 1.0 for class_name in sorted(exact_matches)}
    if fuzzy_matches:
        return dict(sorted(fuzzy_matches.items()))

    return {class_name: 0.1 for class_name in modified_classes}


def associate_test_to_classes(test_id: str, modified_classes: List[str]) -> List[str]:
    affinity_scores = class_affinity_scores(test_id, modified_classes)
    if not affinity_scores:
        return []
    best_affinity = max(affinity_scores.values())
    return sorted(
        class_name
        for class_name, score in affinity_scores.items()
        if score >= best_affinity
    )


def serialize_affinity_scores(scores: Dict[str, float]) -> str:
    return ";".join(
        f"{class_name}={score:.4f}" for class_name, score in sorted(scores.items())
    )


def parse_affinity_scores(text: str) -> Dict[str, float]:
    scores: Dict[str, float] = {}
    for item in str(text).split(";"):
        if not item or "=" not in item:
            continue
        class_name, score = item.rsplit("=", 1)
        try:
            scores[class_name] = float(score)
        except ValueError:
            continue
    return scores


def build_bug_metadata(bug_ids: Iterable[int]) -> pd.DataFrame:
    active = parse_active_bugs().rename(
        columns={
            "bug.id": "bug_id",
            "revision.id.buggy": "revision_buggy",
            "revision.id.fixed": "revision_fixed",
            "report.id": "report_id",
            "report.url": "report_url",
        }
    )

    rows = []
    for bug_id in bug_ids:
        bug_row = active.loc[active["bug_id"] == bug_id]
        if bug_row.empty:
            continue
        row = bug_row.iloc[0].to_dict()
        modified_classes = parse_modified_classes(bug_id)
        relevant_tests = read_nonempty_lines(JSOUP_ROOT / "relevant_tests" / str(bug_id))
        trigger_path = JSOUP_ROOT / "trigger_tests" / str(bug_id)
        triggering_tests = parse_trigger_file(trigger_path)
        trigger_stack_classes = parse_trigger_stack_classes(trigger_path)
        patch_stats = parse_src_patch_stats(bug_id)
        row.update(
            {
                "project_id": "Jsoup",
                "modified_classes": ";".join(modified_classes),
                "relevant_tests": ";".join(relevant_tests),
                "triggering_tests": ";".join(triggering_tests),
                "triggering_test_classes": ";".join(trigger_classes(triggering_tests)),
                "trigger_stack_classes": ";".join(trigger_stack_classes),
                "src_patch_total_changed": sum(item.changed for item in patch_stats.values()),
                "src_patch_total_hunks": sum(item.hunks for item in patch_stats.values()),
                "src_patch_total_files": len(patch_stats),
            }
        )
        rows.append(row)

    return pd.DataFrame(rows)


def build_test_instances(bug_metadata: pd.DataFrame) -> pd.DataFrame:
    records = []
    for row in bug_metadata.itertuples(index=False):
        modified_classes = [item for item in str(row.modified_classes).split(";") if item]
        relevant_tests = [item for item in str(row.relevant_tests).split(";") if item]
        triggering_classes_set = {
            item for item in str(row.triggering_test_classes).split(";") if item
        }
        trigger_stack_classes = {
            item for item in str(row.trigger_stack_classes).split(";") if item
        }
        patch_stats = parse_src_patch_stats(int(row.bug_id))

        for test_id in relevant_tests:
            affinity_scores = class_affinity_scores(test_id, modified_classes)
            if test_id in triggering_classes_set:
                for class_name in trigger_stack_classes:
                    if class_name in affinity_scores:
                        affinity_scores[class_name] = 1.0
            associated_classes = associate_test_to_classes(test_id, modified_classes)
            associated_changes = [
                patch_stats[class_name].changed
                for class_name in associated_classes
                if class_name in patch_stats
            ]
            associated_hunks = [
                patch_stats[class_name].hunks
                for class_name in associated_classes
                if class_name in patch_stats
            ]
            records.append(
                {
                    "project_id": row.project_id,
                    "bug_id": int(row.bug_id),
                    "revision_buggy": row.revision_buggy,
                    "revision_fixed": row.revision_fixed,
                    "test_id": test_id,
                    "is_triggering": int(test_id in triggering_classes_set),
                    "associated_class_count": len(associated_classes),
                    "associated_classes": ";".join(associated_classes),
                    "associated_changed_lines": sum(associated_changes),
                    "associated_hunks": sum(associated_hunks),
                    "class_affinity_scores": serialize_affinity_scores(affinity_scores),
                    "best_affinity": max(affinity_scores.values()) if affinity_scores else 0.0,
                }
            )

    return pd.DataFrame(records)


def compute_failure_history(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["bug_id", "test_id"]).copy()
    failures_before = []
    executions_before = []
    history: Dict[str, tuple[int, int]] = {}

    for row in df.itertuples(index=False):
        failed, executed = history.get(row.test_id, (0, 0))
        failures_before.append(failed)
        executions_before.append(executed)
        history[row.test_id] = (failed + int(row.is_triggering), executed + 1)

    df["failures_before"] = failures_before
    df["executions_before"] = executions_before
    df["failure_history_raw"] = 0.0
    mask = df["executions_before"] > 0
    df.loc[mask, "failure_history_raw"] = (
        df.loc[mask, "failures_before"] / df.loc[mask, "executions_before"]
    )
    return df


def compute_change_frequency(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["bug_id", "test_id"]).copy()
    scores: List[float] = []

    for row in df.itertuples(index=False):
        affinity_scores = parse_affinity_scores(row.class_affinity_scores)
        if not affinity_scores:
            scores.append(0.0)
            continue
        weighted_sum = 0.0
        for class_name, affinity in affinity_scores.items():
            weighted_sum += git_commit_touch_count(row.revision_buggy, class_name) * affinity
        scores.append(weighted_sum)

    df["change_frequency_raw"] = scores
    return df


def compute_complexity_proxy(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    scores: List[float] = []
    for row in df.itertuples(index=False):
        affinity_scores = parse_affinity_scores(row.class_affinity_scores)
        if not affinity_scores:
            scores.append(0.0)
            continue
        weighted_sum = 0.0
        for class_name, affinity in affinity_scores.items():
            metrics = git_source_metrics(row.revision_buggy, class_name)
            patch_bonus = row.associated_hunks if class_name in str(row.associated_classes).split(";") else 0
            weighted_sum += (metrics.score + patch_bonus) * affinity
        scores.append(weighted_sum)
    df["complexity_raw"] = scores
    return df


def min_max_normalize(series: pd.Series) -> pd.Series:
    min_value = series.min()
    max_value = series.max()
    if pd.isna(min_value) or pd.isna(max_value) or min_value == max_value:
        return pd.Series([0.0] * len(series), index=series.index)
    return (series - min_value) / (max_value - min_value)


def normalize_within_bug(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["failure_history_norm"] = df.groupby("bug_id")["failure_history_raw"].transform(
        min_max_normalize
    )
    df["change_frequency_norm"] = df.groupby("bug_id")["change_frequency_raw"].transform(
        min_max_normalize
    )
    df["complexity_norm"] = df.groupby("bug_id")["complexity_raw"].transform(
        min_max_normalize
    )
    return df


def compute_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["risk_score"] = (
        0.40 * df["failure_history_norm"]
        + 0.35 * df["change_frequency_norm"]
        + 0.25 * df["complexity_norm"]
    )
    return df


def rank_group(group: pd.DataFrame, score_column: str, random_seed: int) -> pd.DataFrame:
    ranked = group.copy()
    ranked["_tie_break"] = (
        pd.Series(range(len(ranked)), index=ranked.index)
        .sample(frac=1.0, random_state=random_seed)
        .rank(method="first")
    )
    ranked = ranked.sort_values(
        [score_column, "_tie_break"], ascending=[False, True]
    ).reset_index(drop=True)
    ranked["rank"] = range(1, len(ranked) + 1)
    return ranked.drop(columns=["_tie_break"])


def rank_random_group(group: pd.DataFrame, random_seed: int) -> pd.DataFrame:
    ranked = group.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)
    ranked["rank"] = range(1, len(ranked) + 1)
    return ranked


def apfd_from_ranked_group(group: pd.DataFrame) -> float:
    n = len(group)
    fault_positions = group.loc[group["is_triggering"] == 1, "rank"].tolist()
    m = len(fault_positions)
    if n == 0 or m == 0:
        return float("nan")
    return 1 - (sum(fault_positions) / (n * m)) + (1 / (2 * n))


def run_all_methods(df: pd.DataFrame, random_seed: int = 527) -> tuple[pd.DataFrame, pd.DataFrame]:
    methods = {
        "Random": None,
        "FailureHistory": "failure_history_norm",
        "ChangeFrequency": "change_frequency_norm",
        "ComplexityOnly": "complexity_norm",
        "Proposed": "risk_score",
    }

    ranked_outputs = []
    summary_rows = []

    for bug_id, bug_group in df.groupby("bug_id"):
        for method_name, score_column in methods.items():
            if score_column is None:
                ranked = rank_random_group(bug_group, random_seed=random_seed + int(bug_id))
            else:
                ranked = rank_group(
                    bug_group,
                    score_column=score_column,
                    random_seed=random_seed + int(bug_id),
                )
            ranked = ranked.copy()
            ranked["method"] = method_name
            ranked_outputs.append(ranked)
            summary_rows.append(
                {
                    "bug_id": int(bug_id),
                    "method": method_name,
                    "apfd": apfd_from_ranked_group(ranked),
                    "num_tests": len(ranked),
                    "num_triggering": int(ranked["is_triggering"].sum()),
                }
            )

    return pd.concat(ranked_outputs, ignore_index=True), pd.DataFrame(summary_rows)
