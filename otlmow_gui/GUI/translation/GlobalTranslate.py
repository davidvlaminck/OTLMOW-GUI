from pathlib import Path

from otlmow_gui.Domain.enums import Language
from otlmow_gui.Domain.Settings import Settings


class GlobalTranslate:
    instance = None

    def __init__(self,settings:dict,lang_dir:Path):
        self._ = Settings.return_language(lang_dir,Language[settings["language"]])
        GlobalTranslate.instance = self

    @classmethod
    def _(cls,key:str) -> str:
        return cls.instance._(key)

    def get_all(self):
        return self._