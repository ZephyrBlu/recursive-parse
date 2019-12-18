from pathlib import Path, PurePath
import re
import json
from fuzzywuzzy import fuzz
from zephyrus_sc2_parser import parse_replay
import logging


def recursive_parse(
    *, sub_dir=None, data_function, player_match=None, identifier_rules=[]
):
    """
    Function that recurses through directories
    to find replay files and then parse them
    """

    logging.basicConfig(filename='recursive_parse.log', level=logging.DEBUG)
    path = Path().absolute() / sub_dir
    global_match_info = []

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

    standard_player_match = [
        ('\\w+ +[v,V][s,S]\\.? +\\w+', 'search'),
        ('.vs\\.?.', 'split'),
    ]

    if player_match is None:
        player_match = standard_player_match
    elif player_match is False:
        player_match = []

    def recurse(path, player_names=[], identifiers=[]):
        if path.is_dir():
            logging.debug(f'In dir: {PurePath(path).name}')
            logging.debug(f'Path: {path}\n')
            # iterate through subdirectories and recurse
            for item in path.iterdir():
                item_path_str = PurePath(item).name

                # See if dir is an identifier
                try:
                    for rule_name, rule in identifier_rules:
                        match = re.search(rule, item_path_str)
                        if match:
                            identifiers.append((rule_name, match.group()))
                            break
                except ValueError as error:
                    logging.critical('Error: rule does not follow format (<name>, <rule>)')
                    logging.critical(f'{error}\n')
                    return

                # Regex to parse player names from dir name
                current_name_str = item_path_str
                for rule, rule_type in player_match:
                    if not current_name_str:
                        break

                    if rule_type == 'search':
                        current_name_str = re.search(rule, current_name_str)
                        if current_name_str:
                            current_name_str = current_name_str.group()

                    elif rule_type == 'split':
                        current_name_str = re.split(rule, current_name_str)

                        if current_name_str and type(current_name_str) is list:
                            player_names = current_name_str

                # if dir, recurse
                recurse(item, player_names, identifiers)
        elif path.is_file():
            path_str = PurePath(path)
            logging.debug(f'Found file: {path_str.name}')
            logging.debug(path)
            for index, p in enumerate(player_names):
                logging.debug(f'Player {index}: {p}\n')
            logging.debug('\n')
            players, timeline, stats, metadata = parse_replay(
                path_str, local=True, detailed=True
            )

            if player_match:
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
            else:
                name_id_matches = {}

            match_info = data_function(
                players,
                timeline,
                stats,
                metadata,
                name_id_matches=name_id_matches,
                identifiers=identifiers,
                ignore_units=standard_ignore_units,
                merge_units=standard_merge_units,
            )
            global_match_info.extend(match_info)
        else:
            logging.error('Error: Not a file or directory')
    recurse(path)

    with open('match_info.json', 'w', encoding='utf-8') as output:
        json.dump({'match_info': global_match_info}, output)
