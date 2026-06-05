from abc import abstractmethod
from typing import Generator

from ..Exceptions.CanNotClearAttributeError import CanNotClearAttributeError


class WaardenObject:
    @abstractmethod
    def __init__(self):
        self._parent = None
        self._is_waarden_object: bool = True

    def __iter__(self) -> Generator:
        for k, v in vars(self).items():
            if k in {'_parent', '_geometry_types', '_valid_relations', '_is_waarden_object', '_is_union_waarden_object'}:
                continue
            yield v
