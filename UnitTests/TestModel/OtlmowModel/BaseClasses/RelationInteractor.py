from abc import abstractmethod
from pathlib import Path

from otlmow_model.OtlmowModel.Helpers.generated_lists import get_hardcoded_class_dict, get_concrete_subclasses_from_class_dict


class RelationInteractor:
    typeURI = ''
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def add_valid_relation(self, relation: str, target: str, direction: str = 'o', deprecated: str = ''):
        if relation not in self._valid_relations:
            self._valid_relations[relation] = {}
        if target not in self._valid_relations[relation]:
            self._valid_relations[relation][target] = {}
        self._valid_relations[relation][target][direction] = deprecated

    @abstractmethod
    def __init__(self):
        super().__init__()

        self._valid_relations = {}

    def _get_all_concrete_relations(self, model_directory: Path = None):
        class_dict = get_hardcoded_class_dict(model_directory)
        for relation in self._valid_relations:
            for target in self._valid_relations[relation]:
                for direction, deprecated in self._valid_relations[relation][target].items():
                    if class_dict[target]['abstract']:
                        for subclass in get_concrete_subclasses_from_class_dict(target, model_directory=model_directory):
                            if direction == 'o':
                                yield self.typeURI, relation, subclass, '', deprecated
                            elif direction == 'i':
                                yield subclass, relation, self.typeURI, '', deprecated
                            elif direction == 'u':
                                yield self.typeURI, relation, subclass, 'Unspecified', deprecated
                    else:
                        if direction == 'o':
                            yield self.typeURI, relation, target, '', deprecated
                        elif direction == 'i':
                            yield target, relation, self.typeURI, '', deprecated
                        elif direction == 'u':
                            yield self.typeURI, relation, target, 'Unspecified', deprecated
