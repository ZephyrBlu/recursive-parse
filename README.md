# Recursive Replay Parsing for Tournament Replay Packs

This is a script for parsing tournament replay packs. It recursively searches sub-directories for replay files, then parses the replays using the [Zephyrus Replay Parser](https://github.com/ZephyrBlu/zephyrus-sc2-parser).

You can inject a function to analyze output data. Analyzed data is aggregated and stored, then exported as JSON.

Information from directory names such as group, BoX and player names can be also be parsed and associated with replay data.

## Installation and Usage

This script is hosted on PyPI and can be installed with pip

`pip install recursive_parse`

The `recursive_parse` function is imported by default

`import recursive_parse`

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

`merge_units` is a dictionary in the format of: `<unit name>: <changed name>`. It can be used to merge information from different unit modes or to re-name a unit, such as `LurkerMP` --> `Lurker`.

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

