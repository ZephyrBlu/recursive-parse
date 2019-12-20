from pathlib import Path, PurePath
import re
import json
import copy
import logging
from sc2_tournament_analysis.defaults import standard_player_match
from sc2_tournament_analysis.handle_replay import handle_replay


def recursive_parse(
    *,
    sub_dir=None,
    data_function,
    player_match=None,
    identifier_rules=[],
    multi=False,
):
    """
    Function that recurses through directories
    to find replay files and then parse them
    """

    logging.basicConfig(filename='recursive_parse.log', level=logging.DEBUG)
    path = Path().absolute() / sub_dir
    match_info_paths = []
    global_match_info = []

    if player_match is None:
        player_match = standard_player_match
    elif player_match is False:
        player_match = []

    def check_dir_name(path_str, player_names, identifiers):
        # See if dir is an identifier
        try:
            for rule_name, rule in identifier_rules:
                match = re.search(rule, path_str)
                if match and (rule_name, match.group()) not in identifiers:
                    identifiers.append((rule_name, match.group()))
                    break
        except ValueError as error:
            logging.critical('Error: rule does not follow format (<name>, <rule>)')
            logging.critical(f'{error}\n')
            return

        # Regex to parse player names from dir name
        current_name_str = path_str
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
                else:
                    player_names = None
        return player_names

    def recurse(path, player_names=[], identifiers=[]):
        if path.is_dir():
            logging.debug(f'In dir: {PurePath(path).name}')
            logging.debug(f'Path: {path}\n')
            current_path_str = PurePath(path).name
            result = check_dir_name(
                current_path_str, player_names, identifiers
            )
            if result:
                player_names = result

            # iterate through subdirectories and recurse
            for item in path.iterdir():
                item_path_str = PurePath(item).name
                item_identifiers = copy.deepcopy(identifiers)
                result = check_dir_name(
                    item_path_str, player_names, item_identifiers
                )
                if result:
                    player_names = result

                # if dir, recurse
                recurse(item, player_names, item_identifiers)
        elif path.is_file():
            logging.debug(f'Found file: {PurePath(path).name}')
            logging.debug(path)
            for index, p in enumerate(player_names):
                logging.debug(f'Player {index}: {p}\n')
            logging.debug('\n')

            if multi:
                match_info_paths.append((path, player_names, identifiers))
            else:
                match_info = handle_replay(
                    path,
                    player_names,
                    identifiers,
                    data_function=data_function,
                    player_match=player_match,
                )
                global_match_info.extend(match_info)
        else:
            logging.error('Error: Not a file or directory')
    recurse(path)

    if multi:
        return match_info_paths

    with open('match_info.json', 'w', encoding='utf-8') as output:
        json.dump({'match_info': global_match_info}, output)
