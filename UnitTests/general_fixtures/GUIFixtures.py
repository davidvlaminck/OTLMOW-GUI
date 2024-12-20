from pathlib import Path
from unittest.mock import Mock

from _pytest.fixtures import fixture

from Domain import global_vars
from GUI.screens.DataVisualisationScreen import DataVisualisationScreen
from GUI.translation.GlobalTranslate import GlobalTranslate


@fixture
def create_translations() -> None:
    lang_dir = Path(Path(__file__).absolute()).parent.parent.parent / 'locale/'
    setting={"language": "DUTCH"}
    GlobalTranslate(settings=setting,lang_dir=str(lang_dir))

@fixture
def mock_step3_visuals() -> None:
    step3_visuals = Mock(step3_visuals=DataVisualisationScreen)
    main_window = Mock(step3_visuals=step3_visuals)
    global_vars.otl_wizard = Mock(main_window=main_window)