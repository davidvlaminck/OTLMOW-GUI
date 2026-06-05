from typing import Union

from .OTLObject import OTLObject, OTLAttribuut


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
    if hasattr(obj, 'return_is_otl_object') and obj.return_is_otl_object():
        return _meta_info_otl_object(obj)
    elif hasattr(obj, 'is_otl_attribute') and obj.is_otl_attribute:
        return _meta_info_attribute(obj)
    return None


def _meta_info_otl_object(otl_object: OTLObject) -> str:
    object_string = f'Showing metadata of {otl_object.__class__.__name__}:\n' \
                    f'typeURI: {getattr(otl_object, "typeURI", "")}\n' \
                    f'definition: {otl_object.__doc__}\n'

    if hasattr(otl_object, 'deprecated_version') and getattr(otl_object, 'deprecated_version', None):
        object_string += f'deprecated since {otl_object.deprecated_version}\n'

    object_string += 'attributes:\n'

    for attr in otl_object:
        attr_line = f'    {getattr(attr, "naam", "")} (type: {getattr(getattr(attr, "field", None), "naam", "")})'
        if hasattr(attr, 'deprecated_version') and getattr(attr, 'deprecated_version', ''):
            attr_line += f' <deprecated since {attr.deprecated_version}>'
        object_string += attr_line + '\n'

    return object_string[:-1]


def _meta_info_attribute(attribute: OTLAttribuut) -> str:
    object_string = f'Showing metadata of {getattr(attribute, "naam", "")}:\n' \
                    f'typeURI: {getattr(attribute, "objectUri", "")}\n' \
                    f'definition: {getattr(attribute, "definition", "")}\n'

    if hasattr(attribute, 'deprecated_version') and getattr(attribute, 'deprecated_version', ''):
        object_string += f'deprecated since {attribute.deprecated_version}\n'

    field = getattr(attribute, 'field', None)
    if callable(field):
        field = field()

    if hasattr(field, 'options'):
        object_string += f'valid values:\n'
        options = getattr(field, 'options', {})
        for i, k in enumerate(options.keys()):
            object_string += f'    {k}' + '\n'
            if i >= 9:
                naam = getattr(field, 'naam', '')
                codelist = getattr(field, 'codelist', '')
                object_string += (f'    ...\nFor the full list, review the '
                                  f'class {naam} or go to {codelist}\n')
                break

    waardeObject = getattr(field, 'waardeObject', None)
    if waardeObject is not None:
        object_string += f'attributes:\n'
        for attr in waardeObject():
            attr_line = f'    {getattr(attr, "naam", "")} (type: {getattr(getattr(attr, "field", None), "naam", "")}'
            kard_min = getattr(attr, 'kardinaliteit_min', '1')
            kard_max = getattr(attr, 'kardinaliteit_max', '1')
            if kard_min != '1' or kard_max != '1':
                attr_line += f', cardinality: {kard_min}-{kard_max}'
            attr_line += ')'
            if hasattr(attr, 'deprecated_version') and getattr(attr, 'deprecated_version', ''):
                attr_line += f' <deprecated since {attr.deprecated_version}>'
            object_string += attr_line + '\n'

    return object_string[:-1]
