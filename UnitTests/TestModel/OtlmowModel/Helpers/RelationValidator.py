import inspect
import warnings
from pathlib import Path
from typing import Type, Optional

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import dynamic_create_instance_from_uri
from otlmow_model.OtlmowModel.BaseClasses.RelationInteractor import RelationInteractor
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject
from otlmow_model.OtlmowModel.Exceptions.RelationDeprecationWarning import RelationDeprecationWarning


def is_valid_relation_instance(source: RelationInteractor, relation_instance: RelatieObject,
                               target: RelationInteractor, model_directory: Path = None) -> bool:
    """
    Verifies if a relation would be valid between a source and a target, given the instance of that relation

    :param source: the intended source for the relation
    :type: RelationInteractor
    :param relation_instance: the instance of the relation
    :type: RelatieObject
    :param target: the intended target for the relation
    :type: RelationInteractor
    :param model_directory: directory where the model is located, defaults to otlmow_model's own model
    :type: str
    :return: 'True' if the relation would be valid, 'False' otherwise
    """
    return is_valid_relation(source=source, target=target, relation_type=type(relation_instance),
                             model_directory=model_directory)


def is_valid_relation(relation_type: Type[RelatieObject], source: Optional[RelationInteractor] = None,
                      source_typeURI: Optional[str] = None, target: Optional[RelationInteractor] = None,
                      target_typeURI: Optional[str] = None, model_directory: Path = None) -> bool:
    """
    Verifies if a relation would be valid between a source and a target, given a relation_type type. Exactly one of
    source or source_typeURI must not be None. Exactly one of target or target_typeURI must not be None.

    :param relation_type: the intended type of the relation
    :param source: the intended source for the relation_type
    :type: RelationInteractor
    :param source_typeURI: the typeURI of the intended source for the relation
    :type: str
    :param target: the intended source for the relation
    :type: RelationInteractor
    :param target_typeURI: the typeURI of the intended target for the relation
    :type: str
    :param model_directory: directory where the model is located, defaults to otlmow_model's own model
    :type: str
    :return: 'True' if the relation would be valid, 'False' otherwise
    """

    if source is not None and source_typeURI is not None:
        warnings.warn('both source and source_typeURI are not None. Overriding source by instantiating it',
                      RuntimeWarning)
        source = dynamic_create_instance_from_uri(class_uri=source_typeURI, model_directory=model_directory)
    if target is not None and target_typeURI is not None:
        warnings.warn('both target and target_typeURI are not None. Overriding target by instantiating it',
                      RuntimeWarning)
        target = dynamic_create_instance_from_uri(class_uri=target_typeURI, model_directory=model_directory)

    if source is not None and source_typeURI is None:
        source_typeURI = source.typeURI
    if source_typeURI is None:
        raise ValueError('Exactly one of source or source_typeURI needs to be not None.')

    if target is not None and target_typeURI is None:
        target_typeURI = target.typeURI
    if target_typeURI is None:
        raise ValueError('Exactly one of target or target_typeURI needs to be not None.')

    if 'lgc.' in source_typeURI or 'lgc.' in target_typeURI:
        return True

    if source is None:
        source = dynamic_create_instance_from_uri(class_uri=source_typeURI, model_directory=model_directory)

    if relation_type.typeURI not in source._valid_relations:
        return False

    targets = source._valid_relations[relation_type.typeURI].keys()
    if target_typeURI in targets:
        if 'i' in source._valid_relations[relation_type.typeURI][target_typeURI]:
            return False
        deprecated_value = list(source._valid_relations[relation_type.typeURI][target_typeURI].values())[0]
        if deprecated_value != '':
            warnings.warn(
                message=f'the relation_type of type {relation_type.typeURI} between assets of types '
                        f'{source_typeURI} and {target_typeURI} is deprecated since version {deprecated_value}',
                category=RelationDeprecationWarning)
        return True

    if target is None:
        target = dynamic_create_instance_from_uri(class_uri=target_typeURI, model_directory=model_directory)
    bases = inspect.getmro(type(target))
    for base in bases:
        base_type_uri = _get_member(base, 'typeURI')
        if base_type_uri in targets:
            if 'i' in source._valid_relations[relation_type.typeURI][base_type_uri]:
                return False
            deprecated_value = list(source._valid_relations[relation_type.typeURI][base_type_uri].values())[0]
            if deprecated_value != '':
                warnings.warn(
                    message=f'the relation_type of type {relation_type.typeURI} between assets of types '
                            f'{source_typeURI} and {target_typeURI} is deprecated since version {deprecated_value}',
                    category=RelationDeprecationWarning)
            return True

    return False


def _get_member(obj, name):
    return next(iter([member for _name, member in inspect.getmembers(obj) if name == _name]), None)
