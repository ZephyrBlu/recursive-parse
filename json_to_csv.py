import json
import csv

"""
data schema:

GameID: int (UUID),
Map: str,
Duration: float (minutes)
Group: char/null,
PlayerName: str,
IsWinner: bool,
Race: str ('Protoss', 'Terran', 'Zerg')
UnitName: str,
Produced: int,
Killed: int,

"""

with open('match_info.json', 'r', encoding='utf-8') as data:
    match_info = json.load(data)['match_info']

csv_rows = [(
    'GameID',
    'Map',
    'Duration',
    'Group',
    'PlayerName',
    'IsWinner',
    'Race',
    'UnitName',
    'Produced',
    'Killed',
)]

for unit_record in match_info:
    csv_rows.append(tuple(value for value in unit_record.values()))

with open('match_info.csv', 'w', encoding='utf-8') as output:
    writer = csv.writer(output, lineterminator='\n')
    writer.writerows(csv_rows)
