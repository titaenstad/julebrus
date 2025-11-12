#!/usr/bin/env python3
"""
Script to generate a julebrus table from a list of strings.
"""

import argparse
import string
from pathlib import Path
import pandas as pd


def main():
    """Main function to parse arguments and create the julebrus table."""
    parser = argparse.ArgumentParser(
        description="Create a julebrus table from a list of strings"
    )
    parser.add_argument(
        "brusnavn", nargs="+", help="List of julebrus names to add to the table"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="data/table_data/julebrus.tsv",
        help="Output file path (default: data/table_data/julebrus.tsv)",
    )

    args = parser.parse_args()

    # Create DataFrame with the brusnavn column
    kodenavn = list(string.ascii_uppercase[: len(args.brusnavn)])
    df = pd.DataFrame({"brusnavn": args.brusnavn, "kodenavn": kodenavn})

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save to TSV file
    df.to_csv(output_path, sep="\t", index=False)

    print(f"Successfully created julebrus table with {len(df)} entries")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
