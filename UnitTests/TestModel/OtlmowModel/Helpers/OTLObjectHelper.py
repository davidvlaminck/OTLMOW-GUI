import base64
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Iterable, List, Dict

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, create_dict_from_asset, get_attribute_by_name, \
    dynamic_create_instance_from_ns_and_name
from otlmow_model.OtlmowModel.Helpers.GenericHelper import validate_guid
from otlmow_model.OtlmowModel.Helpers.generated_lists import get_hardcoded_relation_dict


def count_assets_by_type(objects: Iterable[OTLObject]) -> defaultdict:
    d = defaultdict(int)
    for i in objects:
        d[i.typeURI] += 1
    return d


def print_overview_assets(objects: Iterable[OTLObject]) -> None:
    for k, v in count_assets_by_type(objects).items():
        print(f'counting {str(v)} assets of type {k}')


# TODO move to converter (this is using a dotnotation)
def remove_duplicates_in_iterable_based_on_property(iterable: Iterable[OTLObject], property_name: str) -> []:
    d = {}
    for asset in iterable:
        item = asset
        last = property_name
        while '.' in last:
            first = last.split('.')[0]
            last = last.split('.', 1)[1]
            if hasattr(item, first):
                item = getattr(item, first)
                if isinstance(item, list):
                    raise NotImplementedError(
                        "can't use remove_duplicates_in_iterable_based_on_property() when the property value is a list")
        if hasattr(item, last):
            item_prop = getattr(item, last)
            if isinstance(item_prop, list):
                raise NotImplementedError(
                    "can't use remove_duplicates_in_iterable_based_on_property() when the property value is a list")
            item_prop_str = str(item_prop)
            if item_prop_str not in d:
                d[item_prop_str] = asset
    return list(d.values())


def compare_two_lists_of_objects_object_level(first_list: List[OTLObject], second_list: List[OTLObject],
                                              model_directory=None) -> List:
    """Given two lists of objects return the differences from the second list compared to the first list.
    Returns full objects from the second list when unmatched with the first list. """
    l1 = list(map(lambda x: create_dict_from_asset(x), first_list))
    l2 = list(map(lambda x: create_dict_from_asset(x), second_list))
    diff_list = [d for d in l2 if d not in l1]
    return list(map(lambda x: OTLObject.from_dict(x, model_directory), diff_list))


def custom_dict_diff(first_dict, second_dict):
    diff_dict = {}
    for k, v in second_dict.items():
        orig_v = first_dict.get(k)
        if orig_v is None:
            diff_dict[k] = v
            continue
        if orig_v != v:
            if isinstance(v, dict) and isinstance(orig_v, dict):
                result_dict = custom_dict_diff(orig_v, v)
                if result_dict != {}:
                    diff_dict[k] = custom_dict_diff(orig_v, v)
            else:
                diff_dict[k] = v
    return diff_dict


def compare_two_lists_of_objects_attribute_level(first_list: List[OTLObject], second_list: List[OTLObject],
                                                 model_directory: Path = None) -> List:
    """
    Given two lists of objects return the differences from the second list compared to the first list.
    Assumes both lists have objects with a unique assetId. Returns partial objects (on attribute level)
    from the second list when unmatched with the first list. """
    if model_directory is None:
        current_file_path = Path(__file__)
        model_directory = current_file_path.parent.parent.parent

    l1 = list(map(lambda x: create_dict_from_asset(x), first_list))
    verify_asset_id_is_unique_within_list(l1)

    l2 = list(map(lambda x: create_dict_from_asset(x), second_list))
    verify_asset_id_is_unique_within_list(l2)

    l1_dict_list = {dict_asset['assetId']['identificator']: dict_asset for dict_asset in l1}
    l1_dict_list_keys = list(l1_dict_list.keys())

    diff_list = []
    for d in l2:
        asset_id = d['assetId']['identificator']
        if asset_id not in l1_dict_list_keys:
            diff_list.append(d)
            continue
        orig_dict = l1_dict_list[asset_id]
        if orig_dict == d:
            continue
        diff_dict = custom_dict_diff(orig_dict, d)
        if diff_dict == {}:
            continue
        diff_dict['assetId'] = {'identificator': asset_id}
        diff_dict['typeURI'] = orig_dict['typeURI']
        diff_list.append(diff_dict)

    return list(map(lambda x: OTLObject.from_dict(x, model_directory), diff_list))


def verify_asset_id_is_unique_within_list(dict_list: List[Dict]) -> bool:
    d = {}
    for asset_dict in dict_list:
        asset_id = asset_dict['assetId']['identificator']
        if asset_id is None:
            raise ValueError(f'This list has a None value for assetId for at least one asset in this list:\n'
                             f'{asset_dict}')
        asset_d = d.get(asset_id)
        if asset_d is not None:
            raise ValueError(f"There are non-unique assetId's in assets in this list: {asset_id}")
        d[asset_dict['assetId']['identificator']] = asset_dict
    return True


def is_relation(otl_object: OTLObject, model_directory=Path(__file__).parent.parent.parent) -> bool:
    type_uri = otl_object.typeURI
    relation_dict = get_hardcoded_relation_dict(model_directory=model_directory)
    if type_uri in relation_dict:
        return True


def is_directional_relation(otl_object: OTLObject, model_directory=Path(__file__).parent.parent.parent) -> bool:
    type_uri = otl_object.typeURI
    relation_dict = get_hardcoded_relation_dict(model_directory=model_directory)
    relation_info = relation_dict.get(type_uri)
    if relation_info is None:
        return False
    return relation_dict[type_uri]['directional']


def is_aim_id(aim_id: str, model_directory: Path = None) -> bool:
    """
    Checks if the aim_id is valid. An aim_id is valid if it is a valid guid followed by a base64 encoded shortened uri.
    :param aim_id: the aim_id to be validated
    :type aim_id: str
    :param model_directory: directory where the model is located, defaults to otlmow_model's own model
    :type model_directory: Path
    :return: 'True' if the aim_id is valid, 'False' otherwise
    :rtype: bool
    """
    if not aim_id:
        return False
    if len(aim_id) < 38:
        return False

    uuid = aim_id[:36]
    short_uri_encoded = aim_id[37:]

    if not validate_guid(uuid):
        return False
    if not short_uri_encoded:
        return False

    if missing_padding := len(short_uri_encoded) % 4:
        short_uri_encoded += '=' * (4 - missing_padding)

    short_uri_bytes = base64.b64decode(short_uri_encoded)
    try:
        short_uri = short_uri_bytes.decode('ascii')
    except UnicodeDecodeError:
        return False
    try:
        if short_uri == 'purl:Agent':
            return True
        ns, name = short_uri.split('#')
        instance = dynamic_create_instance_from_ns_and_name(ns, name, model_directory=model_directory)
        return instance is not None
    except ModuleNotFoundError:
        warnings.warn('Could not import the module for the given aim_id, did you forget the model_directory?', category=ImportWarning)
        return False
    except ValueError:
        return False
