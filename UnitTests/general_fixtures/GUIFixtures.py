from pathlib import Path
from unittest.mock import Mock

import pytest
from _pytest.fixtures import fixture

from otlmow_gui.Domain import global_vars
from otlmow_gui.GUI.screens.DynamicDataVisualisationScreen import DynamicDataVisualisationScreen
from otlmow_gui.GUI.translation.GlobalTranslate import GlobalTranslate


@fixture
def create_translations() -> None:
    lang_dir = Path(Path(__file__).absolute()).parent.parent.parent / 'otlmow_gui' / 'locale/'
    setting={"language": "DUTCH"}
    GlobalTranslate(settings=setting,lang_dir=str(lang_dir))

@pytest.fixture(scope="function")
def mock_step3_visuals() -> None:
    step3_visuals = Mock(step3_visuals=DynamicDataVisualisationScreen)
    main_window = Mock(step3_visuals=step3_visuals)
    global_vars.otl_wizard = Mock(main_window=main_window)