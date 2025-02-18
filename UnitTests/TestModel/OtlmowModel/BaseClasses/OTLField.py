from abc import abstractmethod
from typing import Any


class OTLField:
    waarde_shortcut_applicable: bool = False
    naam: str = ''
    label: str = ''
    objectUri: str = ''
    definition: str = ''
    usagenote: str = ''
    deprecated_version: str = ''
    waardeObject: Any = None
    clearing_value: Any = None

    @classmethod
    def validate(cls, value: Any, attribuut) -> bool:
        if not attribuut.field.waardeObject:
            return
        if isinstance(value, list):
            for list_item in value:
                if not isinstance(list_item, attribuut.field.waardeObject):
                    raise ValueError(
                        f'{attribuut.objectUri} is a complex datatype. Set the values through the attributes. '
                        f'Use .attr_type_info() for more info')
        elif not isinstance(value, attribuut.field.waardeObject):
            raise ValueError(
                f'{attribuut.objectUri} is a complex datatype. Set the values through the attributes. '
                f'Use .attr_type_info() for more info')
        validation = True
        for attr in value:
            if attr.waarde is None:
                continue
            if attr.kardinaliteit_max != '1':
                for value_item in attr.waarde:
                    if not attr.field.validate(value_item, attr):
                        validation = False
                        break
            elif not attr.field.validate(attr.waarde, attr):
                validation = False
                break
        return validation

    @classmethod
    def value_default(cls, value: Any) -> Any:
        return value

    @classmethod
    def convert_to_correct_type(cls, value: Any, log_warnings: bool = True) -> Any:
        return value

    @abstractmethod
    def __str__(self) -> str:
        return f"""information about {self.naam}:
naam: {self.naam}
uri: {self.objectUri}
definition: {self.definition}
label: {self.label}
usagenote: {self.usagenote}
deprecated_version: {self.deprecated_version}"""

    @classmethod
    def create_dummy_data(cls):
        raise NotImplementedError()
