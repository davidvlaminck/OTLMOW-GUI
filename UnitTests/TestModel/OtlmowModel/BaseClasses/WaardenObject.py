from abc import abstractmethod
from typing import Generator

from otlmow_model.OtlmowModel.Exceptions.CanNotClearAttributeError import CanNotClearAttributeError


class WaardenObject:
    @abstractmethod
    def __init__(self):
        self._parent = None

    def __iter__(self) -> Generator:
        for k, v in vars(self).items():
            if k in ['_parent', '_geometry_types', '_valid_relations']:
                continue
            yield v
