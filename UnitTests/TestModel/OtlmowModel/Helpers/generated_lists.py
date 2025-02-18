import json
from pathlib import Path
from typing import Dict

global_relation_dict: Dict = {}

ROOT_PATH = Path(__file__).parent


def get_hardcoded_relation_dict(relation_dict: Dict = None):
    if relation_dict is None:
        relation_dict = global_relation_dict

    if relation_dict == {}:
        # open json file
        with open(ROOT_PATH.parent / 'generated_info.json', 'r') as f:
            relation_dict = json.load(f)

    return relation_dict
