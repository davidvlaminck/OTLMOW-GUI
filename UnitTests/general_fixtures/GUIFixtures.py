from pathlib import Path

from _pytest.fixtures import fixture

from GUI.translation.GlobalTranslate import GlobalTranslate


@fixture
def create_translations() -> None:
    lang_dir = Path(Path(__file__).absolute()).parent.parent.parent / 'locale/'
    setting={"language": "DUTCH"}
    GlobalTranslate(settings=setting,lang_dir=str(lang_dir))