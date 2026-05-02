from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pdfplumber


def pdf_tables_to_csv(pdf_path: Path, csv_path: Path) -> int:
    """Extract tables from every PDF page into a single CSV file."""
    row_count = 0
    with pdfplumber.open(pdf_path) as pdf, csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    writer.writerow(row)
                    row_count += 1
    return row_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract PDF tables into CSV.")
    parser.add_argument("pdf_path", type=Path)
    parser.add_argument("csv_path", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = pdf_tables_to_csv(args.pdf_path, args.csv_path)
    print(f"Wrote {rows} rows to {args.csv_path}")


if __name__ == "__main__":
    main()
