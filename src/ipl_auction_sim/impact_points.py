from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_WEIGHTS = {2022: 0.1, 2023: 0.3, 2024: 0.6}
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
IMPACT_DATA_DIR = RAW_DATA_DIR / "impact"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def weighted_impact(player_name: str, impact_files: dict[int, Path], weights: dict[int, float]) -> float:
    """Return a weighted impact score for seasons where the player has innings data."""
    total_points = 0.0
    total_weight = 0.0

    for year, file_path in impact_files.items():
        table = pd.read_csv(file_path)
        match = table.loc[table["Player"] == player_name]
        if match.empty:
            continue

        innings = float(match.iloc[0]["Inns"])
        if innings <= 0:
            continue

        weight = weights[year]
        total_points += float(match.iloc[0]["BI"]) * weight
        total_weight += weight

    return total_points / total_weight if total_weight else 0.0


def build_weighted_auction_file(
    auction_file: Path,
    batter_files: dict[int, Path],
    bowler_files: dict[int, Path],
    output_file: Path,
    weights: dict[int, float] | None = None,
) -> pd.DataFrame:
    """Add batting and bowling impact columns to the auction player pool."""
    weights = weights or DEFAULT_WEIGHTS
    auction = pd.read_csv(auction_file).copy()

    auction["BaI"] = auction["Name"].apply(lambda name: weighted_impact(name, batter_files, weights))
    auction["BoI"] = auction["Name"].apply(lambda name: weighted_impact(name, bowler_files, weights))

    output_file.parent.mkdir(parents=True, exist_ok=True)
    auction.to_csv(output_file, index=False)
    return auction


def default_impact_files(kind: str) -> dict[int, Path]:
    return {
        year: IMPACT_DATA_DIR / f"most_impactful_{kind}_{year}.csv"
        for year in DEFAULT_WEIGHTS
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build weighted IPL auction player impact ratings.")
    parser.add_argument("--auction-file", type=Path, default=RAW_DATA_DIR / "Auction.csv")
    parser.add_argument("--output-file", type=Path, default=PROCESSED_DATA_DIR / "Updated_Auction_Weighted.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_weighted_auction_file(
        auction_file=args.auction_file,
        batter_files=default_impact_files("batters"),
        bowler_files=default_impact_files("bowlers"),
        output_file=args.output_file,
    )
    print(f"Wrote {len(result)} weighted auction rows to {args.output_file}")


if __name__ == "__main__":
    main()
