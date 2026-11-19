"""Write a .hy3 file's results (or entries) to CSV: python main.py <file.hy3> <output_dir>"""

import argparse
from pathlib import Path

from hyparse import read_hy3
from hyparse.dataframes import entries_df, relay_results_df, results_df, splits_df


def hy3_to_csv(file_name: str, output_dir: str) -> None:
    hy3 = read_hy3(file_name)
    out = Path(output_dir)
    name = hy3.meet.name or Path(file_name).stem
    if hy3.kind == "entries":
        entries_df(hy3).to_csv(out / f"{name}_entries.csv", index=False)
    else:
        results_df(hy3).to_csv(out / f"{name}_individual_results.csv", index=False)
        relay_results_df(hy3).to_csv(out / f"{name}_relay_results.csv", index=False)
        splits_df(hy3).to_csv(out / f"{name}_splits.csv", index=False)
    print(f"Wrote {name} ({hy3.kind}) to {out}; {len(hy3.issues)} issue(s)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file_name", help="Path to the .hy3 file")
    parser.add_argument("output_dir", help="Directory to save the CSV files")
    args = parser.parse_args()
    hy3_to_csv(args.file_name, args.output_dir)
