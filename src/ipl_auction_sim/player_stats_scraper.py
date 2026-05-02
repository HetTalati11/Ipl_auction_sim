from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup


SEARCH_URL = "https://search.espncricinfo.com/ci/content/site/search.html"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "player_profiles"


def search_player_profile(player_name: str) -> str | None:
    response = requests.get(
        SEARCH_URL,
        params={"search": player_name},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "/cricketers/" not in href:
            continue
        return href if href.startswith("https://") else f"https://www.espncricinfo.com{href}"

    return None


def scrape_player_stats(profile_url: str) -> pd.DataFrame:
    response = requests.get(profile_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")
    if table is None:
        raise ValueError(f"No stats table found at {profile_url}")

    rows = []
    for row in table.find_all("tr"):
        cells = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
        if cells:
            rows.append(cells)

    if len(rows) < 2:
        raise ValueError(f"Stats table at {profile_url} did not contain data rows")

    return pd.DataFrame(rows[1:], columns=rows[0])


def safe_filename(player_name: str) -> str:
    return re.sub(r"\W+", "", player_name) + ".csv"


def scrape_players_from_csv(player_csv: Path, output_dir: Path = OUTPUT_DIR) -> list[Path]:
    players = pd.read_csv(player_csv)["Name"].dropna().tolist()
    output_dir.mkdir(parents=True, exist_ok=True)
    written_files = []

    for player_name in players:
        profile_url = search_player_profile(player_name)
        if profile_url is None:
            print(f"Profile not found: {player_name}")
            continue

        stats = scrape_player_stats(profile_url)
        output_file = output_dir / safe_filename(player_name)
        stats.to_csv(output_file, index=False)
        written_files.append(output_file)
        print(f"Wrote {output_file}")

    return written_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape ESPNcricinfo profile stats for auction players.")
    parser.add_argument("player_csv", type=Path, help="CSV containing a Name column.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scrape_players_from_csv(args.player_csv, args.output_dir)


if __name__ == "__main__":
    main()
