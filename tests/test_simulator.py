import pandas as pd

from ipl_auction_sim.simulator import simulate_auction


def test_simulate_auction_sells_players_to_available_teams() -> None:
    players = pd.DataFrame(
        [
            {
                "SetNo_": 1,
                "Name": "Auction Player",
                "Overseas": 0,
                "MOB": "MOB",
                "BasePrice": 20,
                "BaI": 30,
                "BoI": 0,
            }
        ]
    )

    result = simulate_auction(players, teams=["CSK"])

    assert result.loc[0, "Team"] == "CSK"
    assert result.loc[0, "SoldPrice"] >= 20
