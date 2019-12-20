from fuzzywuzzy import fuzz
from zephyrus_sc2_parser import parse_replay
from sc2_tournament_analysis.defaults import (
    standard_ignore_units, standard_merge_units
)


def handle_replay(
    path, player_names, identifiers, *, data_function, player_match=None
):
    players, timeline, stats, metadata = parse_replay(
        path, local=True, detailed=True
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
    return match_info
