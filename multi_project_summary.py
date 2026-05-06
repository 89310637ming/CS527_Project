from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"


def load_results(filename: str, dataset: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    df = pd.read_csv(path)
    df["dataset"] = dataset
    return df


def main() -> None:
    lang = load_results("lang_apfd_results.csv", "Lang")
    math = load_results("math_apfd_results.csv", "Math")
    jsoup = load_results("jsoup_apfd_results.csv", "Jsoup")
    combined = pd.concat([lang, math, jsoup], ignore_index=True)
    combined.to_csv(DATA_DIR / "combined_apfd_results.csv", index=False)

    summary = (
        combined.groupby(["dataset", "method"], as_index=False)["apfd"]
        .agg(["mean", "median"])
        .reset_index()
    )
    overall = (
        combined.groupby("method", as_index=False)["apfd"]
        .agg(["mean", "median"])
        .reset_index()
        .sort_values("mean", ascending=False)
    )

    print("Per-dataset summary")
    print(summary.to_string(index=False))
    print("\nCombined summary")
    print(overall.to_string(index=False))


if __name__ == "__main__":
    main()
