# IPL Auction Simulator

A mock IPL auction project. It combines IPL auction pool data with ESPNcricinfo impact tables, downweights older seasons, and runs a simple demand-based auction simulation across IPL teams.

## What It Does

- Builds weighted batting and bowling impact ratings from the 2022, 2023, and 2024 IPL seasons.
- Enriches the auction player pool with `BaI` and `BoI` scores.
- Simulates an auction using player roles, overseas status, base prices, team budgets, and basic squad needs.
- Keeps raw data, processed outputs, and reusable source code in a clean repo structure.

## Project Structure

```text
data/
  raw/
    Auction.csv
    impact/
      most_impactful_batters_2022.csv
      most_impactful_bowlers_2022.csv
      ...
    player_profiles/
      individual ESPNcricinfo player profile CSVs
  processed/
    Updated_Auction_Weighted.csv
    noBat.csv
    notPlayed.csv
src/ipl_auction_sim/
  impact_points.py
  simulator.py
  player_stats_scraper.py
  pdf_to_csv.py
tests/
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux, activate with `source .venv/bin/activate`.

## Rebuild Player Ratings

```bash
python -m ipl_auction_sim.impact_points
```

This reads `data/raw/Auction.csv` and the impact files in `data/raw/impact/`, then writes:

```text
data/processed/Updated_Auction_Weighted.csv
```

The default weights are:

| Season | Weight |
| --- | ---: |
| 2022 | 0.1 |
| 2023 | 0.3 |
| 2024 | 0.6 |

## Run The Auction Simulation

```bash
python -m ipl_auction_sim.simulator
```

The simulator writes:

```text
data/processed/simulated_auction_results.csv
```

## Notes

This is still a work-in-progress exploratory project. 
