import json
from collections.abc import Iterable
from pathlib import Path

global_relation_dict_by_model: dict = {}
global_class_dict_by_model: dict = {}

MODEL_ROOT_PATH = Path(__file__).parent.parent.parent


def get_hardcoded_relation_dict(model_directory: Path = None) -> dict:
    global global_relation_dict_by_model
    model_dir_str = str(model_directory)
    if model_dir_str in global_relation_dict_by_model:
        return global_relation_dict_by_model[model_dir_str]

    if model_directory is None:
        model_directory = MODEL_ROOT_PATH
        model_dir_str = str(model_directory)

    generated_info_path = model_directory / 'OtlmowModel' / 'generated_info.json'
    if not generated_info_path.exists():
        raise FileNotFoundError(f"Generated info file not found at {generated_info_path}")

    with open(generated_info_path) as f:
        generated_info_dict = json.load(f)
    global_relation_dict_by_model[model_dir_str] = generated_info_dict['relations']

    return global_relation_dict_by_model[model_dir_str]


def get_hardcoded_class_dict(model_directory: Path = None) -> dict:
    global global_class_dict_by_model
    model_dir_str = str(model_directory)
    if model_dir_str in global_class_dict_by_model:
        return global_class_dict_by_model[model_dir_str]

    if model_directory is None:
        model_directory = MODEL_ROOT_PATH
        model_dir_str = str(model_directory)

    generated_info_path = model_directory / 'OtlmowModel' / 'generated_info.json'
    if not generated_info_path.exists():
        raise FileNotFoundError(f"Generated info file not found at {generated_info_path}")

    with open(generated_info_path) as f:
        generated_info_dict = json.load(f)
    global_class_dict_by_model[model_dir_str] = generated_info_dict['classes']

    return global_class_dict_by_model[model_dir_str]

def get_concrete_subclasses_from_class_dict(base_uri: str, model_directory: Path = None) -> Iterable[str]:
    class_dict = get_hardcoded_class_dict(model_directory)
    for subclass in class_dict[base_uri]['direct_subclasses']:
        if not class_dict[subclass]['abstract']:
            yield subclass
        yield from get_concrete_subclasses_from_class_dict(subclass, model_directory)