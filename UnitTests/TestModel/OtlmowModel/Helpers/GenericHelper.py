import base64
import re
from typing import Optional, Match

from otlmow_model.OtlmowModel.BaseClasses.URIField import URIField


def get_shortened_uri(object_uri: str):
    if object_uri == 'http://purl.org/dc/terms/Agent':
        return 'purl:Agent'
    if '/ns/' not in object_uri:
        raise ValueError(f'{object_uri} is not a valid uri to extract a namespace from')
    shorter_uri = object_uri.split('/ns/')[1]
    if object_uri.startswith('https://lgc.'):
        return f'lgc:{shorter_uri}'
    return shorter_uri


def get_ns_and_name_from_uri(object_uri):
    if object_uri == 'http://purl.org/dc/terms/Agent':
        return 'purl', 'Agent'
    short_uri = get_shortened_uri(object_uri)
    short_uri_array = short_uri.split('#')
    ns, name = short_uri_array[0], short_uri_array[1]
    if ns.startswith('lgc:'):
        if '.' in name:
            name = name.replace('.', '_')
        if '-' in name:
            name = name.replace('-', '_')
        if name == "RIS":
            name = "RISLegacy"
        elif name == 'Fietstel':
            name = 'FietstelLegacy'
        elif name == 'Brug':
            name = 'BeweegbareBrug'
        elif name == 'Voedingskeuzeschakelaar':
            name = 'VKS'
        return 'legacy', name
    return ns, name


def get_class_directory_from_ns(ns):
    return f'Classes/{get_titlecase_from_ns(ns)}'


def get_titlecase_from_ns(ns: str) -> str:
    ns = ns.lower()
    if ns == 'purl':
        return None
    elif ns == 'abstracten':
        return 'Abstracten'
    elif ns == 'implementatieelement':
        return 'ImplementatieElement'
    elif ns == 'installatie':
        return 'Installatie'
    elif ns == 'legacy':
        return 'Legacy'
    elif ns == 'levenscyclus':
        return 'Levenscyclus'
    elif ns == 'onderdeel':
        return 'Onderdeel'
    elif ns == 'proefenmeting':
        return 'ProefEnMeting'
    else:
        raise ValueError()


def get_aim_id_from_uuid_and_typeURI(uuid: str, type_uri: str):
    if not validate_guid(uuid):
        raise ValueError(f'uuid {uuid} is not a valid guid format.')

    if not URIField.validate(type_uri, None):
        raise ValueError(f'type_uri {type_uri} is not a valid uri format.')

    if type_uri == 'http://purl.org/dc/terms/Agent':
        encoded_uri = encode_short_uri('purl:Agent')
    else:
        ns, name = get_ns_and_name_from_uri(type_uri)
        if 'lgc.' in type_uri:
            encoded_uri = encode_short_uri(f'lgc:installatie#{name}')
        else:
            encoded_uri = encode_short_uri(f'{ns}#{name}')
    return f'{uuid}-{encoded_uri}'


def validate_guid(uuid: str) -> Optional[Match]:
    uuid_pattern = "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    return re.match(uuid_pattern, uuid)


def encode_short_uri(short_uri: str) -> str:
    short_uri_bytes = short_uri.encode('ascii')
    base64_bytes = base64.b64encode(short_uri_bytes)
    base64_short_uri = base64_bytes.decode('ascii')
    while base64_short_uri.endswith('='):
        base64_short_uri = base64_short_uri[:-1]
    return base64_short_uri
