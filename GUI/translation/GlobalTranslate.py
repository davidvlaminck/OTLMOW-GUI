

from Domain.enums import Language
from Domain.language_settings import return_language


class GlobalTranslate:
    instance = None

    def __init__(self,settings:dict,lang_dir:str):
        self._ = return_language(lang_dir,Language[settings["language"]])
        GlobalTranslate.instance = self

    @classmethod
    def _(cls,key:str) -> str:
        return cls.instance._(key)

    def getAll(self):
        return self._