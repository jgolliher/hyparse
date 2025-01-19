# hyparse

Extract results from  `.hy3` results file. 

HY3 files are the standardfor swim meet management and each result file offers rich and interesting data. Extracting this data, however, is difficult. **Hyparse** is a Python-based tool for extracting data from `.hy3` files into a JSON or a Pandas DataFrame.


## Usage

The folder `hyparse` contains classes and methods for extraction. For now, the easiest way to use this library is by running `main.py` with your own custom arguments set. Another way to to create a separate python file within the root of the repository and running the code from there.

### Option #1: Use Terminal

The following will extract individual and relay results to two separate CSV files in a directory of your choosing.

1. Open Terminal
2. CD to the directory where `main.py` is (e.g., `CD /Users/jgolliher/hyparse`)
3. Run `python main.py "path/to/hy3_file.hy3" "path/to/save/csv_files"` (e.g., `python main.py "data/hy3/Meet Results-2024 Tennessee Invitational-19Nov2024-001.hy3" "data/csv"`)

### Option #2: Separate Python File

After cloning the repo, create a new Python file in the root directory and use the following to extract!

```python
from hyparse import Hy3File

file_name = "data/hy3/Meet Results-2024 Tennessee Invitational-19Nov2024-001.hy3"

file = Hy3File(file_name=file_name)

# Extract meet information to a dict
file.meet_info.to_dict()

# Extract individual results to Pandas DataFrame
file.individual_results_to_df()

# Extract relay results to Pandas DataFrame
file.relay_results_to_df()


# Extract all Athelte objects (returns List[Athlete])
file.athletes

# Extract all Team objects (returns List[Team])
file.teams

# Extract all IndividaulResult objects (returns List[IndividualResult])
file.individual_results

# Extract all RelayResult objects (returns List[RelayResult])
file.relay_results
```

## Up Next

This continues to be an initial pass at extraction. I need to work on a few things, namely:

* ~~Relay extraction~~  **Done!**
* Split extraction
* Team scores (though I'm not sure if this is stored in the .hy3 file)
* Code cleanup and better object-oriented programming
* Make outputted dataframe more customizable

I'd also like to build a PostgreSQL database that stores all processed meets, but that's another project :) 
