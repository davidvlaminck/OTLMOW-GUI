from typing import Union

from otlmow_model.OtlmowModel.BaseClasses.KeuzelijstField import KeuzelijstField
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, OTLAttribuut


def meta_info(obj: Union[OTLObject, OTLAttribuut], attribute: str = '') -> str:
    """Returns metadata of the object or attribute"""
    if attribute != '':
        if '.' in attribute:
            first = attribute.split('.')[0]
            rest = attribute.split('.', 1)[1]
            if hasattr(obj, '_' + first):
                attr = getattr(obj, '_' + first)
                return meta_info(attr.field.waardeObject(), rest)
            else:
                raise ValueError(f"'{attribute}' does not exist, please check the spelling")
        else:
            if hasattr(obj, '_' + attribute):
                attr = getattr(obj, '_' + attribute)
                return meta_info(attr)
            else:
                raise ValueError(f"'{attribute}' does not exist, please check the spelling")
    if isinstance(obj, OTLObject):
        return _meta_info_otl_object(obj)
    elif isinstance(obj, OTLAttribuut):
        return _meta_info_attribute(obj)


def _meta_info_otl_object(otl_object: OTLObject) -> str:
    object_string = f'Showing metadata of {otl_object.__class__.__name__}:\n' \
                    f'typeURI: {otl_object.typeURI}\n' \
                    f'definition: {otl_object.__doc__}\n'

    if hasattr(otl_object, 'deprecated_version') and otl_object.deprecated_version is not None:
        object_string += f'deprecated since {otl_object.deprecated_version}\n'

    object_string += 'attributes:\n'

    for attr in otl_object:
        attr_line = f'    {attr.naam} (type: {attr.field.naam})'
        if attr.deprecated_version != '':
            attr_line += f' <deprecated since {attr.deprecated_version}>'
        object_string += attr_line + '\n'

    return object_string[:-1]


def _meta_info_attribute(attribute: OTLAttribuut) -> str:
    object_string = f'Showing metadata of {attribute.naam}:\n' \
                    f'typeURI: {attribute.objectUri}\n' \
                    f'definition: {attribute.definition}\n'

    if hasattr(attribute, 'deprecated_version') and attribute.deprecated_version != '':
        object_string += f'deprecated since {attribute.deprecated_version}\n'

    if isinstance(attribute.field(), KeuzelijstField):
        object_string += f'valid values:\n'
        for i, k in enumerate(attribute.field.options.keys()):
            object_string += f'    {k}' + '\n'
            if i >= 9:
                object_string += (f'    ...\nFor the full list, review the '
                                  f'class {attribute.field.naam} or go to {attribute.field.codelist}\n')
                break

    if attribute.field.waardeObject is not None:
        object_string += f'attributes:\n'
        for attr in attribute.field.waardeObject():
            attr_line = f'    {attr.naam} (type: {attr.field.naam}'
            if attr.kardinaliteit_min != '1' or attr.kardinaliteit_max != '1':
                attr_line += f', cardinality: {attr.kardinaliteit_min}-{attr.kardinaliteit_max}'
            attr_line += ')'
            if attr.deprecated_version != '':
                attr_line += f' <deprecated since {attr.deprecated_version}>'
            object_string += attr_line + '\n'

    return object_string[:-1]
