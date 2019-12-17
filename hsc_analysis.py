import uuid
from recursive_parse import recursive_parse

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


def parse_data(players, timeline, stats, metadata, **kwargs):
    name_id_matches = kwargs['name_id_matches']
    identifiers = kwargs['identifiers']
    ignore_units = kwargs['ignore_units']
    merge_units = kwargs['merge_units']

    def check_winner(p_id):
        if metadata['winner'] == p_id:
            return True
        return False

    match_info = []

    current_merged_units = {}
    game_id = str(uuid.uuid4())
    for p_id, player in players.items():
        for obj in player.objects.values():
            if 'unit' not in obj.type or obj.name in ignore_units:
                continue

            if obj.name in merge_units.keys() or obj.name in merge_units.values():
                if obj.name in merge_units.keys():
                    unit_name = merge_units[obj.name]
                elif obj.name in merge_units.values():
                    unit_name = obj.name
            else:
                unit_name = obj.name

            current_unit_info = {
                'game_id': game_id,
                'map': metadata['map'],
                'duration': round(metadata['game_length']/60, 2),
                'player_name': name_id_matches[p_id],
                'is_winner': check_winner(p_id),
                'race': players[p_id].race,
                'unit_name': unit_name,
                # 'produced': info['live'] + info['died'],
                # 'killed': info['died'],
                'birth_time': round(obj.birth_time/22.4/60, 2) if obj.birth_time else None,
                'death_time': round(obj.death_time/22.4/60, 2) if obj.death_time else None,
            }
            for i in identifiers:
                current_unit_info[i[0]] = i[1]
            match_info.append(current_unit_info)

    for unit, info in current_merged_units.items():
        match_info.append(info)

    return match_info


recursive_parse(
    sub_dir='replays',
    data_function=parse_data,
    identifier_rules=[('group', '(?<=Group )\\w{1}(?: *$)')],
)
