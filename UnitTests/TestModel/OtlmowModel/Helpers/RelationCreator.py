import warnings
from pathlib import Path
from typing import Optional

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import dynamic_create_instance_from_uri
from otlmow_model.OtlmowModel.BaseClasses.RelationInteractor import RelationInteractor
from otlmow_model.OtlmowModel.Classes.Agent import Agent
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject
from otlmow_model.OtlmowModel.Classes.Onderdeel.HeeftBetrokkene import HeeftBetrokkene
from otlmow_model.OtlmowModel.Exceptions.CouldNotCreateRelationError import CouldNotCreateRelationError
from otlmow_model.OtlmowModel.Helpers.GenericHelper import get_ns_and_name_from_uri, validate_guid, encode_short_uri, \
    get_aim_id_from_uuid_and_typeURI
from otlmow_model.OtlmowModel.Helpers.RelationValidator import is_valid_relation


def create_relation(relation_type: type[RelatieObject], source: Optional[RelationInteractor] = None,
                    target: Optional[RelationInteractor] = None,
                    source_uuid: Optional[str] = None, source_typeURI: Optional[str] = None,
                    target_uuid: Optional[str] = None, target_typeURI: Optional[str] = None,
                    model_directory: Path = None) -> Optional[RelatieObject]:
    """
    Instantiates a relation, if valid, between instantiated objects, given a specific relation type.
    Instead of instantiated objects, valid guids and typeURI's can be provided, for source and/or target.

    :param relation_type: the relation type of the relation to be created
    :type: RelatieObject
    :param source: the intended source for the relation
    :type: RelationInteractor
    :param target: the intended target for the relation
    :type: RelationInteractor
    :param source_uuid: the uuid of the intended source for the relation
    :type: str
    :param source_typeURI: the typeURI of the intended source for the relation
    :type: str
    :param target_uuid: the uuid of the intended target for the relation
    :type: str
    :param target_typeURI: the typeURI of the intended target for the relation
    :type: str
    :param model_directory: directory where the model is located, defaults to otlmow_model's own model
    :type: str

    :return: Returns the instantiated relation between the given source and target, or None if the relation is invalid.
    :rtype: RelatieObject or None
    """

    if model_directory is None:
        current_file_path = Path(__file__)
        model_directory = current_file_path.parent.parent.parent

    if source is None and (source_typeURI is None or source_uuid is None):
        raise ValueError('Exactly one of source or (source_typeURI + source_uuid) needs to be not None.')
    if target is None and (target_typeURI is None or target_uuid is None):
        raise ValueError('Exactly one of target or (target_typeURI + target_uuid) needs to be not None.')

    if source is not None and source_typeURI is not None:
        warnings.warn('both source and source_typeURI are not None. Using source and ignoring source_typeURI.',
                      RuntimeWarning)
    if target is not None and target_typeURI is not None:
        warnings.warn('both target and target_typeURI are not None. Using source and ignoring target_typeURI.',
                      RuntimeWarning)

    source_is_legacy, target_is_legacy = False, False
    source_aim_id, target_aim_id = None, None

    if source is None:
        if not validate_guid(source_uuid):
            raise ValueError('source_uuid is not a valid guid format.')

        if 'lgc.' in source_typeURI:
            source_is_legacy = True

        source_aim_id = get_aim_id_from_uuid_and_typeURI(source_uuid, source_typeURI)

        if not source_is_legacy:
            source = dynamic_create_instance_from_uri(source_typeURI, model_directory=model_directory)
            if source_typeURI == 'http://purl.org/dc/terms/Agent':
                source.agentId.identificator = source_aim_id
                source.agentId.toegekendDoor = 'AWV'
            else:
                source.assetId.identificator = source_aim_id
                source.assetId.toegekendDoor = 'AWV'

    if target is None:
        if not validate_guid(target_uuid):
            raise ValueError('target_uuid is not a valid guid format.')

        if 'lgc.' in target_typeURI:
            target_is_legacy = True

        target_aim_id = get_aim_id_from_uuid_and_typeURI(target_uuid, target_typeURI)

        if not target_is_legacy:
            target = dynamic_create_instance_from_uri(target_typeURI, model_directory=model_directory)
            if target_typeURI == 'http://purl.org/dc/terms/Agent':
                target.agentId.identificator = target_aim_id
                target.agentId.toegekendDoor = 'AWV'
            else:
                target.assetId.identificator = target_aim_id
                target.assetId.toegekendDoor = 'AWV'

    if not (source_is_legacy or target_is_legacy):
        valid = is_valid_relation(source=source, target=target, relation_type=relation_type)
        if not valid:
            raise CouldNotCreateRelationError("Can't create an invalid relation_type, please validate relations first")

    relation_type = dynamic_create_instance_from_uri(class_uri=relation_type.typeURI,
                                                     model_directory=model_directory)

    if not source_is_legacy:
        if source.typeURI == 'http://purl.org/dc/terms/Agent' and source.agentId.identificator is None:
            raise AttributeError('In order to create a relation_type, the source needs to have a valid agentId '
                                 '(source.agentId.identificator)')
        elif source.typeURI != 'http://purl.org/dc/terms/Agent' and source.assetId.identificator is None:
            raise AttributeError('In order to create a relation_type, the source needs to have a valid assetId '
                                 '(source.assetId.identificator)')
    if not target_is_legacy:
        if target.typeURI == 'http://purl.org/dc/terms/Agent' and target.agentId.identificator is None:
            raise AttributeError('In order to create a relation_type, the target needs to have a valid agentId '
                                 '(target.agentId.identificator)')
        elif target.typeURI != 'http://purl.org/dc/terms/Agent' and target.assetId.identificator is None:
            raise AttributeError('In order to create a relation_type, the target needs to have a valid assetId '
                                 '(target.assetId.identificator)')


    if source_is_legacy:
        relation_type.bronAssetId.identificator = source_aim_id
        relation_type.bronAssetId.toegekendDoor = 'AWV'
        relation_id = source_aim_id
    else:
        if source.typeURI == 'http://purl.org/dc/terms/Agent':
            relation_type.bronAssetId.identificator = source.agentId.identificator
            relation_type.bronAssetId.toegekendDoor = source.agentId.toegekendDoor
            relation_id = source.agentId.identificator
        else:
            relation_type.bronAssetId.identificator = source.assetId.identificator
            relation_type.bronAssetId.toegekendDoor = source.assetId.toegekendDoor
            relation_id = source.assetId.identificator

    relation_id += '_-_'

    if target_is_legacy:
        relation_type.doelAssetId.identificator = target_aim_id
        relation_type.doelAssetId.toegekendDoor = 'AWV'
        relation_id += target_aim_id
    else:
        if target.typeURI == 'http://purl.org/dc/terms/Agent':
            relation_type.doelAssetId.identificator = target.agentId.identificator
            relation_type.doelAssetId.toegekendDoor = target.agentId.toegekendDoor
            relation_id += target.agentId.identificator
        else:
            relation_type.doelAssetId.identificator = target.assetId.identificator
            relation_type.doelAssetId.toegekendDoor = target.assetId.toegekendDoor
            relation_id += target.assetId.identificator

    relation_id = relation_type.__class__.__name__ + '_-_' + relation_id

    relation_type.assetId.identificator = relation_id
    relation_type.assetId.toegekendDoor = 'OTLMOW'

    if source_is_legacy:
        relation_type.bron.typeURI = source_typeURI
    else:
        relation_type.bron.typeURI = source.typeURI

    if target_is_legacy:
        relation_type.doel.typeURI = target_typeURI
    else:
        relation_type.doel.typeURI = target.typeURI

    return relation_type


def create_betrokkenerelation(rol: str, source: Optional[RelationInteractor] = None,
                              target: Optional[Agent] = None,
                              source_uuid: Optional[str] = None, source_typeURI: Optional[str] = None,
                              target_uuid: Optional[str] = None, target_typeURI: Optional[str] = None,
                              model_directory: Path = None) -> Optional[HeeftBetrokkene]:
    relation = create_relation(source=source, target=target, source_uuid=source_uuid, source_typeURI=source_typeURI,
                               target_uuid=target_uuid, target_typeURI=target_typeURI, model_directory=model_directory,
                               relation_type=HeeftBetrokkene)
    relation.rol = rol
    return relation
