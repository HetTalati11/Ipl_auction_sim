from pathlib import Path

import pandas as pd

from ipl_auction_sim.impact_points import build_weighted_auction_file


def test_build_weighted_auction_file_ignores_zero_innings(tmp_path: Path) -> None:
    auction_file = tmp_path / "auction.csv"
    batter_2022 = tmp_path / "batters_2022.csv"
    batter_2023 = tmp_path / "batters_2023.csv"
    bowler_2022 = tmp_path / "bowlers_2022.csv"
    bowler_2023 = tmp_path / "bowlers_2023.csv"
    output_file = tmp_path / "weighted.csv"

    pd.DataFrame(
        [{"SetNo_": 1, "Name": "Test Player", "Overseas": 0, "MOB": "MOB", "BasePrice": 20}]
    ).to_csv(auction_file, index=False)
    pd.DataFrame([{"Player": "Test Player", "BI": 10, "Inns": 0}]).to_csv(batter_2022, index=False)
    pd.DataFrame([{"Player": "Test Player", "BI": 40, "Inns": 8}]).to_csv(batter_2023, index=False)
    pd.DataFrame([{"Player": "Test Player", "BI": 5, "Inns": 4}]).to_csv(bowler_2022, index=False)
    pd.DataFrame([{"Player": "Test Player", "BI": 15, "Inns": 6}]).to_csv(bowler_2023, index=False)

    result = build_weighted_auction_file(
        auction_file=auction_file,
        batter_files={2022: batter_2022, 2023: batter_2023},
        bowler_files={2022: bowler_2022, 2023: bowler_2023},
        output_file=output_file,
        weights={2022: 0.25, 2023: 0.75},
    )

    assert result.loc[0, "BaI"] == 40
    assert result.loc[0, "BoI"] == 12.5
    assert output_file.exists()
