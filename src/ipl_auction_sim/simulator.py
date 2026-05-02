from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "processed" / "Updated_Auction_Weighted.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "processed" / "simulated_auction_results.csv"

ROLE_NEEDS = {
    "WK": 2,
    "MOB": 4,
    "ALR": 3,
    "FB": 3,
    "SPIN": 2,
}

IPL_TEAMS = [
    "CSK",
    "DC",
    "GT",
    "KKR",
    "LSG",
    "MI",
    "PBKS",
    "RCB",
    "RR",
    "SRH",
]


@dataclass
class TeamState:
    name: str
    budget: float = 12000.0
    overseas_slots: int = 8
    role_counts: dict[str, int] = field(default_factory=dict)

    def can_bid(self, player: pd.Series) -> bool:
        if self.budget < float(player["BasePrice"]):
            return False
        return not (int(player["Overseas"]) == 1 and self.overseas_slots <= 0)

    def demand_for(self, player: pd.Series) -> float:
        role = str(player["MOB"])
        target = ROLE_NEEDS.get(role, 2)
        current = self.role_counts.get(role, 0)
        role_gap = max(target - current, 0)
        impact = max(float(player["BaI"]), float(player["BoI"]))
        overseas_penalty = 0.9 if int(player["Overseas"]) == 1 and self.overseas_slots <= 2 else 1.0
        return (impact * 12 + role_gap * 80 + float(player["BasePrice"])) * overseas_penalty

    def buy(self, player: pd.Series, price: float) -> None:
        self.budget -= price
        role = str(player["MOB"])
        self.role_counts[role] = self.role_counts.get(role, 0) + 1
        if int(player["Overseas"]) == 1:
            self.overseas_slots -= 1


def player_rating(player: pd.Series) -> float:
    return max(float(player["BaI"]), float(player["BoI"])) + float(player["BasePrice"]) / 100


def simulate_auction(players: pd.DataFrame, teams: list[str] | None = None) -> pd.DataFrame:
    """Run a deterministic, demand-based mock auction."""
    team_states = [TeamState(name) for name in (teams or IPL_TEAMS)]
    auction_order = players.sort_values(["SetNo_", "BasePrice"], ascending=[True, False]).copy()
    results = []

    for _, player in auction_order.iterrows():
        eligible_teams = [team for team in team_states if team.can_bid(player)]
        if not eligible_teams:
            results.append(result_row(player, "UNSOLD", 0.0))
            continue

        winner = max(eligible_teams, key=lambda team: team.demand_for(player))
        demand = winner.demand_for(player)
        ceiling = min(winner.budget, float(player["BasePrice"]) + demand * 0.08)
        price = min(winner.budget, round(max(float(player["BasePrice"]), ceiling) / 10) * 10)

        winner.buy(player, price)
        results.append(result_row(player, winner.name, price))

    return pd.DataFrame(results)


def result_row(player: pd.Series, team: str, price: float) -> dict[str, object]:
    return {
        "Name": player["Name"],
        "Role": player["MOB"],
        "Overseas": int(player["Overseas"]),
        "BasePrice": float(player["BasePrice"]),
        "BaI": float(player["BaI"]),
        "BoI": float(player["BoI"]),
        "Rating": round(player_rating(player), 2),
        "Team": team,
        "SoldPrice": price,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a mock IPL auction simulation.")
    parser.add_argument("--input-file", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-file", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    players = pd.read_csv(args.input_file)
    results = simulate_auction(players)
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output_file, index=False)
    print(f"Wrote {len(results)} simulated auction rows to {args.output_file}")


if __name__ == "__main__":
    main()
