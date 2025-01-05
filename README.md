# hyparse

Extract results from a HyTek `.hy3` results file. 

HyTek's Meet Manager is the standard for swim meet management and each result file offers rich and interesting data. Extracting this data, however, is difficult. **Hyparse** is a Python-based tool for extracting data from `.hy3` files into a JSON format (CSV coming soon!)

## Usage

The file `hytek_parser.py` contains a class called `HyTekParser` that can be used for extraction. The easiest way, for now, is to clone this repoistory and within the directory create your own Python file and running the following:

```python
from hytek_parser import HyTekParser

file_name = "data/Meet Results-2024 Tennessee Invitational-19Nov2024-001.hy3" #Or your own file

# Example Usage
parser = HyTekParser()
parser.load_file(file_name)

# Save results to a dict
results = parser.results

# Other objects
parser.file_info
parser.athletes
parser.teams
```

## Up Next

This is an *intial* pass at extraction. I need to work on a few things, namely:

* Enabling CSV output
* Split extraction
* Team scores

I'd also like to build a PostgreSQL database that stores all processed meets, but that's another project :) 