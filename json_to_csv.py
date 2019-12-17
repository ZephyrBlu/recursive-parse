import json
import csv

"""
data schema:

GameID: uuid
Map: str
Duration: float (minutes)
PlayerName: str
IsWinner: bool
Race: str ('Protoss', 'Terran', 'Zerg')
UnitName: str
BirthTime: float (minutes)
DeathTime: float (minutes)
"""

with open('match_info_new.json', 'r', encoding='utf-8') as data:
    match_info = json.load(data)['match_info']

csv_rows = [(
    'GameID',
    'Map',
    'Duration',
    'PlayerName',
    'IsWinner',
    'Race',
    'UnitName',
    'BirthTime',
    'DeathTime',
    'Group',
)]

for unit_record in match_info:
    csv_rows.append(tuple(value for value in unit_record.values()))

with open('match_info_new.csv', 'w', encoding='utf-8') as output:
    writer = csv.writer(output, lineterminator='\n')
    writer.writerows(csv_rows)
