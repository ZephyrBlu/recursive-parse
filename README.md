# Replay Parsing for Tournament Replay Packs

This is a (small) library for parsing tournament replay packs. It currently allows you to recursively search sub-directories for replay files, then parse them using the [Zephyrus Replay Parser](https://github.com/ZephyrBlu/zephyrus-sc2-parser).

You can inject a function to analyze output data. Analyzed data is aggregated and stored, then exported as JSON.

Information from directory names such as group, BoX and player names can be also be parsed and associated with replay data.

## Installation and Usage

This script is hosted on PyPI and can be installed with pip

`pip install sc2_tournament_analysis`

You can import the `recursive_parse` and `json_to_csv` functions

`from sc2_tournament_analysis import recursive_parse, json_to_csv`

## Functions

### `recursive_parse`

### Required Arguments

There are 2 required keyword arguments for the function: `sub_dir` and `data_function`.

`sub_dir` specifies the relative path of the replays you want to parse from the location of the script

    dir/
      analysis.py <-- recursive_parse called here
      replays/
        ...
    
    sub_dir = 'replays'

`data_function` is a function supplied by the user to analyze output data from parsed replays. Returned data is appended to a list which is exported as JSON after all replays have been parsed.

You can access all the information available from parsed replay (`players, timeline, stats, metadata`) as well as enclosed information in your supplied function via `kwargs`. This includes default values and any information parsed from directory names.

Defaults currently available are `ignore_units` and `merge_units`.

`ignore_units` is a list of temporary unit which are usually not wanted.

`merge_units` is a dictionary in the format of `<unit name>: <changed name>`. It can be used to merge information from different unit modes or to re-name a unit, such as `LurkerMP` --> `Lurker`.

### Optional Arguments

`recursive_parse` takes 2 optional keyword arguments: `player_match` and `identifiers`. Both are RegEx patterns that parse information from directory names.

`player_match` is specifically for parsing player names from directories. It takes a list of tuples of RegEx patterns and the type of search to perform.

Ex: `(<pattern>, <search type>)`

You can choose between `search` or `split` for search type, but the last pattern must be a `split` to separate the player names.

The default patterns are:

    standard_player_match = [
        ('\\w+ +[v,V][s,S]\\.? +\\w+', 'search'),
        ('.vs\\.?.', 'split'),
    ]
    
`identifiers` is for parsing information from directory names. It contains a list of tuples of RegEx patterns and the chosen name of the pattern. It has no default patterns.

Ex: `(<pattern name>, <pattern>)`

The list of tuples can be accessed through `kwargs['identifier']` in your `data_function`.

### Example

The `hsc_analysis.py` file is an example of usage for replay files from HSC XX.

The `parse_data` function loops through each player's units and buildings that were created during the game and records information about the unit/building and game. It also indentifies and stores groups that players were in.

### `json_to_csv`

Data is exported as JSON to a JSON file by default, but you can use the `json_to_csv.py` file to create a CSV file from the JSON data.

### Required Arguments

There is 1 required positional argument for `json_to_csv`: `headers`

`headers` represents the column names in the CSV file

### Optional Arguments

There is 1 optional keyword argument for `json_to_csv`: `data_function`

-----

**WARNING: If you do not provide a `data_function` function your data generated from `recursive_parse` MUST be a `list` of iterable data (I.e. Either `list` or `tuple` data)**

Ex:

    match_info.json
    
    {
        'match_info': [
            ['this', 'is', 'valid'],
            ('so', 'is', 'this'),
            { 'dicts': 'are not', 'iterable': 'though' }
        ]
    }

-----

Similarly to `recursive_parse`, `data_function` is applied to each record that was generated with `recursive_parse`.

You can use this function to process or make calculations/changes to the data before it is written to CSV format. For instance, flattening a `dict` structure or making a calculation based on multiple values.

Data that is returned from `data_function` represents 1 row/record in the CSV data. Its return value must be iterable and should be the same size as the number of columns you want.

Ex:

    columns = ['Name', 'Age', 'Gender']
    json_to_csv(columns, data_function=some_func)
    
    ...
    
    # record = { 'name': 'John', 'age': 25, 'gender': 'Male']
    def some_func(record):
        # record is not iterable so needs to be processed
        # create an inline generator then cast to tuple to get values
        return tuple(value for value in record.values())
    
