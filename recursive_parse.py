from pathlib import Path, PurePath
import re
import uuid
import json
from fuzzywuzzy import fuzz
from zephyrus_sc2_parser import parse_replay
import logging

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

logging.basicConfig(filename='recursive_parse.log', level=logging.DEBUG)
path = Path().absolute() / 'hsc_replays'
match_info = []

standard_ignore_units = [
    'AdeptPhaseShift',
    'Larva',
    'LocustMP',
    'OracleStasisTrap',
    'Interceptor',
    'MULE',
    'AutoTurret',
    'Egg',
    'TransportOverlordCocoon',
    'OverlordCocoon',
    'LurkerMPEgg',
    'LocustMPFlying',
    'LocustMPPrecursor',
    'InfestedTerransEgg',
    'InfestorTerran',
    'BroodlingEscort',
    'Broodling',
    'RavagerCocoon',
    'BanelingCocoon',
    'BroodLordCocoon',
]

standard_merge_units = {
    'ObserverSiegeMode': 'Observer',
    'WarpPrismPhasing': 'WarpPrism',
    'WidowMineBurrowed': 'WindowMine',
    'SiegeTankSieged': 'SiegeTank',
    'ThorAP': 'Thor',
    'VikingFighter': 'Viking',
    'VikingAssault': 'Viking',
    'LiberatorAG': 'Liberator',
    'OverseerSiegeMode': 'Overseer',
    'OverlordTransport': 'Overlord',
    'LurkerMP': 'Lurker',
    'LurkerMPBurrowed': 'Lurker',
    'SwarmhostMP': 'Swarmhost',
}


def recursive_parse(path, group=None, player_names=None):
    """
    Function that recurses through directories
    to find replay files and then parse them.

    Made specficially for HSC XX replay pack
    """
    if path.is_dir():
        logging.debug(f'In dir: {PurePath(path).name}')
        logging.debug(f'Path: {path}')
        # iterate through subdirectories and recurse
        for item in path.iterdir():
            item_path_str = PurePath(item).name

            # 3 cases:
            #
            # 1) Dir is group folder:
            #     - Set group as current dir group
            #
            # 2) Dir is not group folder, but **IS** subdir of a group folder:
            #     - Keep group and pass down to subdir for replay parsing
            #
            # 3) Dir is not group folder and is **NOT** subdir of a group folder:
            #     - Pass group as None

            if re.search('Group', item_path_str):
                group = item_path_str[-1]
            elif group:
                pass
            else:
                group = None

            # Regex to parse player names from dir name
            series_regex = re.split('.vs[.].', item_path_str)

            # 3 cases:
            #
            # 1) Pattern **IS** in dir name:
            #     - Set player names as parsed names
            #
            # 2) Pattern is **NOT** in dir name, but **IS** subdir of a pattern-matched folder:
            #     - Keep player names and pass down to subdir for replay parsing
            #
            # 3) Pattern is **NOT** in dir name and is **NOT** subdir of a pattern-matched folder:
            #     - Pass player names as None

            if len(series_regex) > 1:
                player_names = series_regex
            elif player_names:
                pass
            else:
                player_names = None

            # if dir, recurse
            recursive_parse(item, group, player_names)
    elif path.is_file():
        path_str = PurePath(path)
        logging.debug(f'Found file: {path_str.name}')
        # logging.debug(f'{path_str}, {group}, Player 1: {player_names[0]}, Player 2: {player_names[1]}')
        players, timeline, stats, metadata = parse_replay(path_str, local=True)

        match_ratios = []
        for p_id, p in players.items():
            # partial_ratio fuzzy matches substrings instead of an exact match
            current_match_ratio = fuzz.partial_ratio(p.name, player_names[0])
            match_ratios.append((p.player_id, p.name, current_match_ratio))

        name_match = max(match_ratios, key=lambda x: x[2])

        # linking matched names to in game names
        name_id_matches = {
            name_match[0]: player_names[0]
        }

        if name_match[0] == 1:
            name_id_matches[2] = player_names[1]
        else:
            name_id_matches[1] = player_names[1]
        logging.debug(name_id_matches)

        # set player unit state as final game state
        unit_state = {
            1: timeline[-1][1]['unit'],
            2: timeline[-1][2]['unit'],
        }

        def check_winner(p_id):
            if metadata['winner'] == p_id:
                return True
            return False

        current_merged_units = {}
        game_id = str(uuid.uuid4())
        for p_id, units in unit_state.items():
            for unit, info in units.items():
                if unit in standard_ignore_units:
                    continue

                if unit in standard_merge_units.keys() or unit in standard_merge_units.values():
                    if unit in standard_merge_units.keys():
                        unit_name = standard_merge_units[unit]
                    elif unit in standard_merge_units.values():
                        unit_name = unit

                    if unit_name not in current_merged_units:
                        current_merged_units[unit_name] = {
                            'game_id': game_id,
                            'map': metadata['map'],
                            'duration': round(metadata['game_length']/60, 2),
                            'group': group,
                            'player_name': name_id_matches[p_id],
                            'is_winner': check_winner(p_id),
                            'race': players[p_id].race,
                            'unit_name': unit_name,
                            'produced': info['live'] + info['died'],
                            'killed': info['died'],
                        }
                    else:
                        current_merged_units[unit_name]['produced'] += info['live'] + info['died']
                        current_merged_units[unit_name]['killed'] += info['died']
                    continue

                current_unit_info = {
                    'game_id': game_id,
                    'map': metadata['map'],
                    'duration': round(metadata['game_length']/60, 2),
                    'group': group,
                    'player_name': name_id_matches[p_id],
                    'is_winner': check_winner(p_id),
                    'race': players[p_id].race,
                    'unit_name': unit,
                    'produced': info['live'] + info['died'],
                    'killed': info['died'],
                }
                match_info.append(current_unit_info)

        for unit, info in current_merged_units.items():
            match_info.append(info)
    else:
        logging.error('Error: Not a directory or file')


recursive_parse(path)


with open('match_info.json', 'w', encoding='utf-8') as output:
    json.dump({'match_info': match_info}, output)
