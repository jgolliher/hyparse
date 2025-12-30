import argparse
from hyparse import Hy3File


def hy3_to_csv(file_name: str, output_loc: str):
    print("Loading file...")
    file = Hy3File(file_name=file_name)
    meet_name = file.meet_info.meet_name
    print(f"Extracting {meet_name} results")
    print("Extracting individual results")
    try:
        individual_results = file.individual_results_to_df()
        individual_results.to_csv(
            f"{output_loc}/{meet_name}_individual_results.csv", index=False
        )
        print("Saved individual results")
    except Exception as e:
        print(f"Failed to save individual results with error: {e}")
    print("Extracting relay results")
    try:
        relay_results = file.relay_results_to_df()
        relay_results.to_csv(f"{output_loc}/{meet_name}_relay_results.csv", index=False)
        print("Saved individual results")
    except Exception as e:
        print(f"Failed to save individual results with error: {e}")
    print(f"Finished processing {meet_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert Hy3 swimming meet results to CSV files."
    )
    parser.add_argument("file_name", help="Path to the Hy3 file")
    parser.add_argument("output_loc", help="Directory to save the CSV files")
    args = parser.parse_args()
    hy3_to_csv(args.file_name, args.output_loc)
