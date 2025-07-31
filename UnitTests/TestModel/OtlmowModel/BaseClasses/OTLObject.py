import importlib
import math
import random
import sys
import warnings
from datetime import date, time
from datetime import datetime
from pathlib import Path
from typing import Union, Dict, List, Generator, TypeVar, Type

from otlmow_model.OtlmowModel.BaseClasses.DateField import DateField
from otlmow_model.OtlmowModel.BaseClasses.DateTimeField import DateTimeField
from otlmow_model.OtlmowModel.BaseClasses.KeuzelijstField import KeuzelijstField
from otlmow_model.OtlmowModel.BaseClasses.OTLField import OTLField
from otlmow_model.OtlmowModel.BaseClasses.TimeField import TimeField
from otlmow_model.OtlmowModel.BaseClasses.URIField import URIField
from otlmow_model.OtlmowModel.BaseClasses.UnionTypeField import UnionTypeField
from otlmow_model.OtlmowModel.BaseClasses.UnionWaarden import UnionWaarden
from otlmow_model.OtlmowModel.Exceptions.AttributeDeprecationWarning import AttributeDeprecationWarning
from otlmow_model.OtlmowModel.Exceptions.CanNotClearAttributeError import CanNotClearAttributeError
from otlmow_model.OtlmowModel.Exceptions.ClassDeprecationWarning import ClassDeprecationWarning
from otlmow_model.OtlmowModel.Exceptions.CouldNotCreateInstanceError import CouldNotCreateInstanceError
from otlmow_model.OtlmowModel.Exceptions.MethodNotApplicableError import MethodNotApplicableError
from otlmow_model.OtlmowModel.Exceptions.NonStandardAttributeWarning import NonStandardAttributeWarning
from otlmow_model.OtlmowModel.Helpers.GenericHelper import get_titlecase_from_ns, get_ns_and_name_from_uri
from otlmow_model.OtlmowModel.Helpers.generated_lists import get_hardcoded_class_dict


class OTLAttribuut:
    def __init__(self, naam: str = '', label: str = '', objectUri: str = '', definition: str = '',
                 constraints: str = '', usagenote: str = '', deprecated_version: str = '', kardinaliteit_min: str = '1',
                 kardinaliteit_max: str = '1', field: Type[OTLField] = OTLField, readonly: bool = False,
                 readonlyValue=None, owner=None):
        super().__init__()
        self.naam: str = naam
        self.label: str = label
        self.objectUri: str = objectUri
        self.definition: str = definition
        self.constraints: str = constraints
        self.usagenote: str = usagenote
        self.deprecated_version: str = deprecated_version
        self.readonly: bool = readonly
        self.kardinaliteit_min: str = kardinaliteit_min
        self.kardinaliteit_max: str = kardinaliteit_max
        self._dotnotation: str  = ''
        self.owner = owner
        self.readonlyValue = None
        self.mark_to_be_cleared: bool = False
        self.waarde = None
        self.field: Type[OTLField] = field

        if self.field.waardeObject:
            def add_empty_value():
                prev_value = self.waarde
                if kardinaliteit_max == '1':
                    if prev_value is None:
                        new_value_object = self.field.waardeObject()
                        new_value_object._parent = self
                        self.set_waarde(new_value_object)
                    else:
                        raise RuntimeError("This attribute does not have a cardinality other than 1, therefore you can "
                                           "only call this method once per instance")
                else:
                    if prev_value is None:
                        prev_value = []
                    new_value_object = self.field.waardeObject()
                    new_value_object._parent = self
                    prev_value.append(new_value_object)
                    self.set_waarde(prev_value)

            self.add_empty_value = add_empty_value

        if kardinaliteit_max != '1':
            def add_value(value):
                l = self.waarde
                if self.waarde is None:
                    l = []
                l.append(value)
                self.set_waarde(l)

            self.add_value = add_value

        if readonly:
            self.__dict__["waarde"] = readonlyValue

    def add_value(self, value):
        raise MethodNotApplicableError(
            "This attribute does not have a cardinality other than 1 so simply assign your value directly instead of "
            "using this method")

    def get_waarde(self):
        if self.field.waardeObject and self.waarde is None:
            self.add_empty_value()
        return self.waarde

    def add_empty_value(self):
        """Helper method for datatypes UnionType, ComplexType, KwantWrd and Dte to add the underlying waarde object"""
        if not self.field.waardeObject:
            raise MethodNotApplicableError(
                "In order to use this method this object must be one of these types: UnionType, ComplexType, KwantWrd, "
                "Dte")

    def clear_value(self) -> None:
        if self.readonly:
            raise ValueError(f'attribute {self.naam} is readonly')
        if self.objectUri in {
            'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMDBStatus.isActief',
            'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMNaamObject.naam',
            'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMToestand.toestand'
        } or self.field.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcIdentificator':
            raise CanNotClearAttributeError(f'attribute {self.naam} can not be cleared')
        if (self.owner is not None and hasattr(self.owner, '_parent') and self.owner._parent.field.objectUri ==
                'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcIdentificator'):
            raise CanNotClearAttributeError(f'attribute {self.naam} can not be cleared')

        # complex takes precedence over cardinality
        # => complex + kard means clearing the value of each sub attribute of each item in the list
        # => complex means clearing the value of each sub attribute
        # => list means clearing the value

        if self.field.waardeObject is not None:
            if self.waarde is None:
                self.add_empty_value()
            if self.kardinaliteit_max != '1':
                for item in self.waarde:
                    for sub_attr in item:
                        if not sub_attr.readonly:
                            sub_attr.clear_value()
            else:
                for sub_attr in self.waarde:
                    if not sub_attr.readonly:
                        sub_attr.clear_value()
        else:
            self.waarde = None
            self.mark_to_be_cleared = True

    def _perform_cardinality_check(self, owner, value, kardinaliteit_max):
        kardinaliteit_min = int(self.kardinaliteit_min)
        if not isinstance(value, list):
            raise TypeError(f'expecting a list in {owner.__class__.__name__}.{self.naam}')
        elif isinstance(value, set):
            raise TypeError(f'expecting a non set type of list in {owner.__class__.__name__}.{self.naam}')
        elif 0 < len(value) < kardinaliteit_min:
            raise ValueError(
                f'expecting at least {kardinaliteit_min} element(s) in {owner.__class__.__name__}.{self.naam}')
        elif len(value) > kardinaliteit_max:
            raise ValueError(
                f'expecting at most {kardinaliteit_max} element(s) in {owner.__class__.__name__}.{self.naam}')

    def set_waarde(self, value, owner=None):
        self._perform_deprecation_check(self)

        if value is None:
            self.waarde = None
            return

        if value == self.field.clearing_value or (self.kardinaliteit_max != '1' and value == '88888888'):
            self.clear_value()
            return

        if self.kardinaliteit_max != '1':
            if self.kardinaliteit_max == '*':
                kardinaliteit_max = math.inf
            else:
                kardinaliteit_max = int(self.kardinaliteit_max)
            self._perform_cardinality_check(owner, value, kardinaliteit_max)
            converted_values = []
            for el_value in value:
                converted_value = self.field.convert_to_correct_type(el_value)
                if issubclass(self.field, KeuzelijstField):
                    converted_value = self.field.convert_to_invulwaarde(converted_value, self.field)

                field_validated = self.field.validate(converted_value, self)
                if not field_validated:
                    raise ValueError(
                        f'invalid value in list for {owner.__class__.__name__}.{self.naam}: {el_value} is not '
                        f'valid, must be valid for {self.field.naam}')
                converted_values.append(converted_value)
            self.waarde = converted_values
        else:
            if self.field.waardeObject is not None and isinstance(value, self.field.waardeObject):
                self.waarde = value
            else:
                converted_value = self.field.convert_to_correct_type(value)
                if issubclass(self.field, KeuzelijstField):
                    converted_value = self.field.convert_to_invulwaarde(converted_value, self.field)
                if self.field.validate(value=converted_value, attribuut=self):
                    self.waarde = converted_value
                else:
                    raise ValueError(
                        f'Could not assign the best effort converted value to {owner.__class__.__name__}.{self.naam}')

        # check if kwant Wrd inside a union type, if so, call clear_props
        if (owner is not None and value is not None and hasattr(owner, 'field') and owner.field.waardeObject is not None
                and (owner.field.waarde_shortcut_applicable and not isinstance(owner.field, UnionTypeField)
                     and owner.owner is not None and isinstance(owner.owner, UnionWaarden))):
            owner.owner.clear_other_props(f'_{owner.naam}')

    @staticmethod
    def _perform_deprecation_check(owner):
        if owner is not None:
            if owner.naam == 'waarde':
                owner = owner.owner._parent

            if hasattr(owner, 'deprecated_version') and owner.deprecated_version != '':
                if hasattr(owner, 'objectUri'):
                    warnings.warn(
                        message=f'{owner.objectUri} is deprecated since version {owner.deprecated_version}',
                        category=AttributeDeprecationWarning)
                elif hasattr(owner, 'typeURI'):
                    warnings.warn(message=f'{owner.typeURI} is deprecated since version {owner.deprecated_version}',
                                  category=AttributeDeprecationWarning)
                else:
                    warnings.warn(
                        message=f'used a class that is deprecated since version {owner.deprecated_version}',
                        category=AttributeDeprecationWarning)

    def __str__(self):
        return (f'information about {self.naam}:\n'
                f'naam: {self.naam}\n'
                f'uri: {self.objectUri}\n'
                f'definition: {self.definition}\n'
                f'label: {self.label}\n'
                f'usagenote: {self.usagenote}\n'
                f'constraints: {self.constraints}\n'
                f'readonly: {self.readonly}\n'
                f'kardinaliteit_min: {self.kardinaliteit_min}\n'
                f'kardinaliteit_max: {self.kardinaliteit_max}\n'
                f'deprecated_version: {self.deprecated_version}\n')

    def fill_with_dummy_data(self):
        if self.readonly:
            return

        if self.field.waardeObject is None:
            if self.naam == 'geometry':
                first_geom_type = self.owner._geometry_types[0]
                if first_geom_type == 'POINT Z':
                    self.set_waarde('POINT Z (200000 200000 0)')
                elif first_geom_type == 'LINESTRING Z':
                    self.set_waarde('LINESTRING Z (200000 200000 0, 200001 200001 1)')
                elif first_geom_type == 'POLYGON Z':
                    self.set_waarde('POLYGON Z ((200000 200000 0, 200001 200001 1, 200002 200002 2, 200000 200000 0))')
            else:
                if self.objectUri == 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#NaampadObject.naampad':
                    naam_attr = get_attribute_by_name(self.owner, 'naam')
                    if naam_attr is not None and naam_attr.waarde is not None:
                        data = f'dummy/{naam_attr.waarde}'
                    else:
                        data = 'dummy/dummy'
                else:
                    data = self.field.create_dummy_data()
                if data is None or self.kardinaliteit_max == '1':
                    self.set_waarde(data)
                else:
                    self.set_waarde([data])
            return
        new_value_object = self.field.waardeObject()
        new_value_object._parent = self

        if isinstance(new_value_object, UnionWaarden):
            selected_attr = random.choice(list(new_value_object))
            selected_attr.fill_with_dummy_data()
        else:
            for a in new_value_object:
                a.fill_with_dummy_data()

        if self.kardinaliteit_max != '1':
            self.set_waarde([new_value_object])
        else:
            self.set_waarde(new_value_object)


T = TypeVar('T', bound='OTLObject')


class OTLObject(object):
    typeURI: str = None
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __setattr__(self, name, value):
        if name != 'typeURI':
            super(OTLObject, self).__setattr__(name, value)
        else:
            if hasattr(self, 'typeURI') and (value is not None or self.typeURI is not None):
                raise ValueError("The typeURI is an OSLOAttribute that indicates the class of the instance. "
                                 "Within a class this value is predefined and cannot be changed.")
            if URIField.validate(value, OTLAttribuut(naam='typeURI')):
                self.__dict__['value'] = value
            else:
                raise ValueError(f'{value} is not a valid value for typeURI.')

    def __init__(self):
        super().__init__()

        if hasattr(self, 'deprecated_version') and self.deprecated_version is not None:
            try:
                warnings.warn(message=f'{self.typeURI} is deprecated since version {self.deprecated_version}',
                              category=ClassDeprecationWarning)
            except KeyError:
                warnings.warn(
                    message=f'used a class ({self.__class__.__name__}) that is deprecated since version {self.deprecated_version}',
                    category=ClassDeprecationWarning)

    def clear_value(self, attribute_name: str) -> None:
        if attribute_name is None:
            raise ValueError('attribute_name is None')
        attr = get_attribute_by_name(self, attribute_name)
        if attr is None:
            raise ValueError(f'attribute {attribute_name} does not exist')
        attr.clear_value()

    def create_dict_from_asset(self, waarde_shortcut: bool = False, rdf: bool = False, cast_datetime: bool = False,
                               warn_for_non_otl_conform_attributes: bool = True,
                               allow_non_otl_conform_attributes: bool = True, ) -> Dict:
        """Converts this asset into a dictionary representation. This is now deprecated, use to_dict instead.

        :param waarde_shortcut: whether to use the waarde shortcut when processing the dictionary, defaults to False
        :type: bool
        :param rdf: whether to generate a dictionary where the keys are the URI's of the attributes
        rather than the names, defaults to False
        :type: bool
        :param cast_datetime: whether to convert dates, times and datetimes to strings, defaults to False
        :type: bool
        :param allow_non_otl_conform_attributes: whether to allow non OTL conform attributes. Raising ValueError if not, Defaults to True
        :type: bool
        :param warn_for_non_otl_conform_attributes: whether to generate warnings when using non OTL conform attributes. Defaults to True
        :type: bool

        :return: returns a dictionary representation of this asset
        :rtype: dict"""
        warnings.warn(message='create_dict_from_asset is deprecated, use to_dict instead',
                      category=AttributeDeprecationWarning)
        return create_dict_from_asset(
            otl_object=self, waarde_shortcut=waarde_shortcut, rdf=rdf, cast_datetime=cast_datetime,
            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes)

    def fill_with_dummy_data(self):
        for attr in self:
            if attr is not None:
                attr.fill_with_dummy_data()

    def __repr__(self):
        return build_string_version(asset=self)

    def __iter__(self) -> Generator[OTLAttribuut, None, None]:
        yield from sorted(filter(lambda v: isinstance(v, OTLAttribuut), (vars(self).values())), key=lambda x: x.naam)

    def __eq__(self, other):
        return (create_dict_from_asset(self, warn_for_non_otl_conform_attributes=False) ==
                create_dict_from_asset(other, warn_for_non_otl_conform_attributes=False))

    def is_instance_of(self, otl_type: type, dynamic_created: bool = False, model_directory: Path = None):
        if dynamic_created:
            if model_directory is None:
                current_file_path = Path(__file__)
                model_directory = current_file_path.parent.parent.parent
            try:
                otl_type_typeURI = getattr(otl_type, 'typeURI')
            except AttributeError:
                return False
            dynamic_created_type = dynamic_create_type_from_uri(otl_type_typeURI, model_directory=model_directory)
            return isinstance(self, dynamic_created_type)

        check = isinstance(self, otl_type)
        if check:
            return True

        try:
            otl_type_typeURI = getattr(otl_type, 'typeURI')
        except AttributeError:
            return False

        t = type(self)
        if t.typeURI == otl_type_typeURI:
            return True
        return issubclass(self.__class__, otl_type)

    @classmethod
    def from_dict(cls: T, input_dict: Dict, model_directory: Path = None, rdf: bool = False,
                  cast_datetime: bool = False, waarde_shortcut: bool = False,
                  allow_non_otl_conform_attributes: bool = True, warn_for_non_otl_conform_attributes: bool = True
                  ) -> T:
        """Alternative constructor. Allows the instantiation of an object using a dictionary. Either start from the
        appropriate class or add a typeURI entry to the dictionary to get an instance of that type.

        :param input_dict: input dictionary, containing key value pairs for the attributes of the instance
        :type: dict
        :param model_directory: directory where the model is located, defaults to otlmow_model's own model
        :type: str
        :param rdf: whether to use uri's as keys instead of the names, defaults to False
        :type: bool
        :param waarde_shortcut: whether to use the waarde shortcut when processing the dictionary, defaults to False
        :type: bool
        :param cast_datetime: whether to convert dates, times and datetimes to strings, defaults to False
        :type: bool
        :param allow_non_otl_conform_attributes: whether to allow non OTL conform attributes. Raising ValueError if not, Defaults to True
        :type: bool
        :param warn_for_non_otl_conform_attributes: whether to generate warnings when using non OTL conform attributes. Defaults to True
        :type: bool
        :return: returns an instance where the values of the attributes matches the given dictionary
        :rtype: OTLObject"""
        if not rdf and 'typeURI' in input_dict:
            type_uri = input_dict['typeURI']
        elif rdf and 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.typeURI' in input_dict:
            type_uri = input_dict['https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.typeURI']
        elif rdf and '@type' in input_dict:
            type_uri = input_dict['@type']
            del input_dict['@type']
        else:
            type_uri = cls.typeURI

        if type_uri is None:
            raise ValueError(
                'typeURI is None. Add a valid typeURI to the input dictionary or change the class you are using "from_dict" from.')

        if model_directory is None:
            current_file_path = Path(__file__)
            model_directory = current_file_path.parent.parent.parent

        try:
            o = dynamic_create_instance_from_uri(type_uri, model_directory=model_directory)
        except TypeError:
            raise ValueError(
                'typeURI is invalid. Add a valid typeURI to the input dictionary or change the class you are using "from_dict" from.')

        for k, v in input_dict.items():
            if k in {'typeURI', 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.typeURI'}:
                continue
            set_value_by_dictitem(o, k, v, waarde_shortcut=waarde_shortcut, rdf=rdf,
                                  cast_datetime=cast_datetime,
                                  allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                                  warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)
        return o

    def to_dict(self, rdf: bool = False, cast_datetime: bool = False, waarde_shortcut: bool = False,
                allow_non_otl_conform_attributes: bool = True, warn_for_non_otl_conform_attributes: bool = True) -> Dict:
        """Converts this asset into a dictionary representation

        :param waarde_shortcut: whether to use the waarde shortcut when processing the dictionary, defaults to False
        :type: bool
        :param rdf: whether to generate a dictionary where the keys are the URI's of the attributes
        rather than the names, defaults to False
        :type: bool
        :param cast_datetime: whether to convert dates, times and datetimes to strings, defaults to False
        :type: bool
        :param allow_non_otl_conform_attributes: whether to allow non OTL conform attributes. Raising ValueError if not, Defaults to True
        :type: bool
        :param warn_for_non_otl_conform_attributes: whether to generate warnings when using non OTL conform attributes. Defaults to True
        :type: bool

        :return: returns a dictionary representation of this asset
        :rtype: dict"""
        return create_dict_from_asset(
            otl_object=self, waarde_shortcut=waarde_shortcut, rdf=rdf, cast_datetime=cast_datetime,
            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes)


def create_dict_from_asset(otl_object: OTLObject, waarde_shortcut=False, rdf: bool = False,
                           cast_datetime: bool = False, allow_non_otl_conform_attributes: bool = True,
                           warn_for_non_otl_conform_attributes: bool = True) -> Dict:
    """Creates a dictionary from an OTLObject with key value pairs for attributes and their values. Saves the type of the object in typeURI (or @type for the RDF dict)

    :param otl_object: input object to be transformed
    :type: OTLObject
    :param waarde_shortcut: whether to use the waarde shortcut when processing the dictionary, defaults to False
    :type: bool
    :param rdf: whether to generate a dictionary where the keys are the URI's of the attributes rather than the names, defaults to False
    :type: bool
    :param cast_datetime: whether to convert dates, times and datetimes to strings, defaults to False
    :type: bool
    :param suppress_warnings_non_standardised_attributes: whether to suppress the warning that are raised because the object has attributes that aren't standardised, defaults to False
    :type: bool
    :param warn_for_non_otl_conform_attributes: whether to generate warnings when using non OTL conform attributes. Defaults to True
    :type: bool

    :return: returns an dictionary where the values of the dictionary matches the given input object
    :rtype: dict"""
    if rdf:
        d = _recursive_create_rdf_dict_from_asset(
            asset=otl_object, waarde_shortcut=waarde_shortcut, cast_datetime=cast_datetime,
            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes)
    else:
        d = _recursive_create_dict_from_asset(
            asset=otl_object, waarde_shortcut=waarde_shortcut, cast_datetime=cast_datetime,
            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes)

    if d is None:
        d = {}
    if rdf:
        d['@type'] = otl_object.typeURI
    else:
        d['typeURI'] = otl_object.typeURI
    return d


def _recursive_create_dict_from_asset(
        asset: Union[OTLObject, OTLAttribuut, list, dict], waarde_shortcut: bool = False,
        cast_datetime: bool = False, warn_for_non_otl_conform_attributes: bool = True,
        allow_non_otl_conform_attributes: bool = True
) -> Union[Dict, List[Dict]]:
    if isinstance(asset, list) and not isinstance(asset, dict):
        l = []
        for item in asset:
            dict_item = _recursive_create_dict_from_asset(
                asset=item, waarde_shortcut=waarde_shortcut, cast_datetime=cast_datetime,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes)
            if dict_item is not None:
                l.append(dict_item)
        return l
    else:
        d = {}
        for attr_key, attr in vars(asset).items():
            if attr_key in {'_parent', '_valid_relations', '_geometry_types'}:
                continue
            if isinstance(attr, OTLAttribuut):
                if not attr.mark_to_be_cleared:
                    if attr.waarde is None:
                        continue
                    if attr.waarde == []:
                        d[attr.naam] = []
                        continue

                if attr.field.waardeObject is not None:  # complex
                    if waarde_shortcut and attr.field.waarde_shortcut_applicable:  # waarde shortcut
                        if isinstance(attr.waarde, list):
                            item_list = []
                            for item in attr.waarde:
                                if item._waarde.mark_to_be_cleared:
                                    item_list.append(item._waarde.field.clearing_value)
                                else:
                                    item_list.append(item._waarde.waarde)
                            if len(item_list) > 0:
                                d[attr.naam] = item_list
                        else:
                            if attr.waarde._waarde.mark_to_be_cleared:
                                dict_item = attr.waarde._waarde.field.clearing_value
                            else:
                                dict_item = attr.waarde.waarde
                            if dict_item is not None:
                                d[attr.naam] = dict_item
                    else:  # regular complex or union
                        dict_item = _recursive_create_dict_from_asset(
                            asset=attr.waarde, waarde_shortcut=waarde_shortcut, cast_datetime=cast_datetime,
                            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
                            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes)
                        if dict_item is not None:
                            d[attr.naam] = dict_item
                else:
                    if attr.mark_to_be_cleared:
                        d[attr.naam] = attr.field.clearing_value
                    elif cast_datetime:
                        if attr.field == TimeField:
                            if isinstance(attr.waarde, list):
                                d[attr.naam] = [time.strftime(list_item, "%H:%M:%S") for list_item in attr.waarde]
                            else:
                                d[attr.naam] = time.strftime(attr.waarde, "%H:%M:%S")
                        elif attr.field == DateField:
                            if isinstance(attr.waarde, list):
                                d[attr.naam] = [date.strftime(list_item, "%Y-%m-%d") for list_item in attr.waarde]
                            else:
                                d[attr.naam] = date.strftime(attr.waarde, "%Y-%m-%d")
                        elif attr.field == DateTimeField:
                            if isinstance(attr.waarde, list):
                                d[attr.naam] = [DateTimeField.value_default(list_item)
                                                for list_item in attr.waarde]
                            else:
                                d[attr.naam] = DateTimeField.value_default(attr.waarde)
                        else:
                            d[attr.naam] = attr.waarde
                    else:
                        d[attr.naam] = attr.waarde
            else:
                if not attr_key.startswith('_'):
                    if allow_non_otl_conform_attributes:
                        if warn_for_non_otl_conform_attributes:
                            warnings.warn(
                                message=f'{attr_key} is a non standardized attribute of {asset.__class__.__name__}. '
                                        f'The attribute will be added on the instance.', stacklevel=2,
                                category=NonStandardAttributeWarning)
                        d[attr_key] = attr
                    else:
                        raise ValueError(f'{attr_key} is a non standardized attribute of {asset.__class__.__name__}. '
                                         f'If you want to allow this, set allow_non_otl_conform_attributes to True.')
                else:
                    raise ValueError(
                        f'{attr_key} is a non standardized attribute of {asset.__class__.__name__}. '
                        f'While this is supported, the key can not start with "_".')

        if len(d.items()) > 0:
            return d


def _recursive_create_rdf_dict_from_asset(
        asset: Union[OTLObject, OTLAttribuut, list, dict], waarde_shortcut: bool = False,
        cast_datetime: bool = False, allow_non_otl_conform_attributes: bool = True,
        warn_for_non_otl_conform_attributes: bool = True) -> Union[Dict, List[Dict]]:
    if isinstance(asset, list) and not isinstance(asset, dict):
        l = []
        for item in asset:
            dict_item = _recursive_create_rdf_dict_from_asset(
                asset=item, waarde_shortcut=waarde_shortcut, cast_datetime=cast_datetime,
                warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
                allow_non_otl_conform_attributes=allow_non_otl_conform_attributes)
            if dict_item is not None:
                l.append(dict_item)
        if len(l) > 0:
            return l
    else:
        d = {}
        for attr_key, attr in vars(asset).items():
            if attr_key in {'_parent', '_valid_relations', '_geometry_types'}:
                continue
            if isinstance(attr, OTLAttribuut):
                if not attr.mark_to_be_cleared:
                    if attr.waarde is None:
                        continue
                    if attr.waarde == []:
                        d[attr.naam] = []
                        continue

                if attr.field.waardeObject is not None:  # complex
                    if waarde_shortcut and attr.field.waarde_shortcut_applicable:
                        if isinstance(attr.waarde, list):
                            item_list = []
                            for item in attr.waarde:
                                if item._waarde.mark_to_be_cleared:
                                    item_list.append(item._waarde.field.clearing_value)
                                else:
                                    item_list.append(item._waarde.waarde)
                            if len(item_list) > 0:
                                d[attr.objectUri] = item_list
                        else:
                            if attr.waarde._waarde.mark_to_be_cleared:
                                dict_item = attr.waarde._waarde.field.clearing_value
                            else:
                                dict_item = attr.waarde.waarde
                            if dict_item is not None:
                                d[attr.objectUri] = dict_item
                    else:
                        if attr.mark_to_be_cleared:
                            for a in attr.waarde:
                                a.mark_to_be_cleared = True

                        dict_item = _recursive_create_rdf_dict_from_asset(
                            asset=attr.waarde, waarde_shortcut=waarde_shortcut, cast_datetime=cast_datetime,
                            warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes,
                            allow_non_otl_conform_attributes=allow_non_otl_conform_attributes)
                        if dict_item is not None:
                            d[attr.objectUri] = dict_item
                else:
                    if attr.mark_to_be_cleared:
                        d[attr.objectUri] = attr.field.clearing_value
                    elif cast_datetime:
                        if attr.field == TimeField:
                            if isinstance(attr.waarde, list):
                                d[attr.objectUri] = [time.strftime(list_item, "%H:%M:%S") for list_item in attr.waarde]
                            else:
                                d[attr.objectUri] = time.strftime(attr.waarde, "%H:%M:%S")
                        elif attr.field == DateField:
                            if isinstance(attr.waarde, list):
                                d[attr.objectUri] = [date.strftime(list_item, "%Y-%m-%d") for list_item in attr.waarde]
                            else:
                                d[attr.objectUri] = date.strftime(attr.waarde, "%Y-%m-%d")
                        elif attr.field == DateTimeField:
                            if isinstance(attr.waarde, list):
                                d[attr.objectUri] = [datetime.strftime(list_item, "%Y-%m-%d %H:%M:%S")
                                                     for list_item in attr.waarde]
                            else:
                                d[attr.objectUri] = datetime.strftime(attr.waarde, "%Y-%m-%d %H:%M:%S")
                        elif issubclass(attr.field, KeuzelijstField):
                            if isinstance(attr.waarde, list):
                                if attr.waarde == [None]:
                                    d[attr.objectUri] = []
                                else:
                                    d[attr.objectUri] = [attr.field.options[list_item].objectUri for list_item in
                                                         attr.waarde]
                            else:
                                d[attr.objectUri] = attr.field.options[attr.waarde].objectUri
                        else:
                            d[attr.objectUri] = attr.waarde
                    elif issubclass(attr.field, KeuzelijstField):
                        if isinstance(attr.waarde, list):
                            if attr.waarde == [None]:
                                d[attr.objectUri] = []
                            else:
                                d[attr.objectUri] = [attr.field.options[list_item].objectUri for list_item in
                                                     attr.waarde]
                        else:
                            d[attr.objectUri] = attr.field.options[attr.waarde].objectUri
                    else:
                        d[attr.objectUri] = attr.waarde
            else:
                if not attr_key.startswith('_'):
                    if allow_non_otl_conform_attributes:
                        if warn_for_non_otl_conform_attributes:
                            warnings.warn(
                                message=f'{attr_key} is a non standardized attribute of {asset.__class__.__name__}. '
                                        f'The attribute will be added on the instance.', stacklevel=2,
                                category=NonStandardAttributeWarning)
                        d[attr_key] = attr
                    else:
                        raise ValueError(f'{attr_key} is a non standardized attribute of {asset.__class__.__name__}. '
                                         f'If you want to allow this, set allow_non_otl_conform_attributes to True.')
                else:
                    raise ValueError(
                        f'{attr_key} is a non standardized attribute of {asset.__class__.__name__}. '
                        f'While this is supported, the key can not start with "_".')

        if len(d.items()) > 0:
            return d


def clean_dict(d) -> Union[Dict, None]:
    """Recursively remove None values and empty dicts from input dict"""
    if d is None:
        return None
    for k in list(d):
        v = d[k]
        if isinstance(v, dict):
            clean_dict(v)
            if len(v.items()) == 0:
                del d[k]
        if v is None:
            del d[k]
    return d


def build_string_version(asset, indent: int = 4) -> str:
    indent = max(indent, 4)
    d = create_dict_from_asset(asset, warn_for_non_otl_conform_attributes=False)
    string_version = '\n'.join(_make_string_version_from_dict(d, level=1, indent=indent, prefix='    '))
    if string_version != '':
        string_version = '\n' + string_version
    return f'<{asset.__class__.__name__}> object\n{" " * indent}typeURI : {asset.typeURI}{string_version}'


def _make_string_version_from_dict(d, level: int = 0, indent: int = 4, list_index: int = -1, prefix: str = '') -> List:
    lines = []

    if list_index != -1:
        index_string = f'[{list_index}]'
        index_string += ' ' * (indent - len(index_string))
        prefix += index_string

    for key in sorted(d):
        if key == 'typeURI':
            continue
        value = d[key]
        if isinstance(value, float) and value == 88888888.0:
            value = '88888888 <value_marked_to_be_cleared>'
        elif str(value) == '88888888':
            value = '88888888 <value_marked_to_be_cleared>'

        if isinstance(value, dict):
            lines.append(f'{prefix}{key} :')
            lines.extend(_make_string_version_from_dict(value, level=level + 1, indent=indent,
                                                        prefix=prefix + ' ' * indent))
        elif isinstance(value, list):
            lines.append(f'{prefix}{key} :')
            for index, item in enumerate(value):
                if index == 10:
                    if len(value) == 11:
                        lines.append(f'{prefix}...(1 more item)')
                    else:
                        lines.append(f'{prefix}...({len(value) - 10} more items)')
                    break
                if isinstance(item, dict):
                    lines.extend(_make_string_version_from_dict(item, level=level, indent=indent, list_index=index,
                                                                prefix=prefix))
                else:
                    index_string = f'[{index}]'
                    index_string += ' ' * (indent - len(index_string))
                    lines.append(prefix + index_string + f'{item}')
        else:
            lines.append(f'{prefix}{key} : {value}')
    return lines


def get_attribute_by_uri(instance_or_attribute, key: str) -> Union[OTLAttribuut, None]:
    return next((v for v in instance_or_attribute if v.objectUri == key), None)


def get_attribute_by_name(instance_or_attribute, key: str) -> Union[OTLAttribuut, None]:
    return getattr(instance_or_attribute, f'_{key}', None)


# dict encoder = asset object to dict
# dict decoder = dict to asset object

def set_value_by_dictitem(instance_or_attribute: Union[OTLObject, OTLAttribuut], key: str, value,
                          waarde_shortcut: bool = False, rdf: bool = False, cast_datetime: bool = False,
                          allow_non_otl_conform_attributes: bool = True,
                          warn_for_non_otl_conform_attributes: bool = True):
    if instance_or_attribute is None:
        raise ValueError('instance_or_attribute cannot be None')
    if key is None or key == '':
        raise ValueError('key cannot be empty')

    if rdf:
        attribute_to_set = get_attribute_by_uri(instance_or_attribute, key)
    else:
        attribute_to_set = get_attribute_by_name(instance_or_attribute, key)

    if attribute_to_set is None:
        if allow_non_otl_conform_attributes:
            if warn_for_non_otl_conform_attributes:
                warnings.warn(
                    message=f'Attribute with name "{key}" can not be found on the given instance or attribute. '
                            'Assuming this is a non standardized attribute. Setting the attribute with setattr',
                    category=NonStandardAttributeWarning)
            setattr(instance_or_attribute, key, value)
            return
        else:
            raise ValueError(f'Attribute with name "{key}" can not be found on the given instance or attribute. '
                             'Assuming this is a non standardized attribute. If you want to allow this, set '
                             'allow_non_otl_conform_attributes to True.')

    if value == attribute_to_set.field.clearing_value or value == [attribute_to_set.field.clearing_value]:
        attribute_to_set.clear_value()
        return

    if attribute_to_set.field.waardeObject is not None:  # complex / union / KwantWrd / dte
        if isinstance(value, list):
            for index, list_item in enumerate(value):
                if attribute_to_set.waarde is None or len(attribute_to_set.waarde) <= index:
                    attribute_to_set.add_empty_value()

                if attribute_to_set.field.waarde_shortcut_applicable and waarde_shortcut:  # dte / kwantWrd
                    if list_item == attribute_to_set.waarde[index]._waarde.field.clearing_value:
                        attribute_to_set.waarde[index]._waarde.clear_value()
                        continue
                    attribute_to_set.waarde[index]._waarde.set_waarde(list_item)

                else:  # complex / union
                    for k, v in list_item.items():
                        set_value_by_dictitem(attribute_to_set.waarde[index], k, v, waarde_shortcut, rdf=rdf,
                                              cast_datetime=cast_datetime,
                                              allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                                              warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

        elif isinstance(value, dict):  # only complex / union possible
            if attribute_to_set.waarde is None:
                attribute_to_set.add_empty_value()

            if attribute_to_set.kardinaliteit_max != '1':
                for k, v in value.items():
                    set_value_by_dictitem(attribute_to_set.waarde[0], k, v, waarde_shortcut, rdf=rdf,
                                          cast_datetime=cast_datetime,
                                          allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                                          warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)
            else:
                for k, v in value.items():
                    set_value_by_dictitem(attribute_to_set.waarde, k, v, waarde_shortcut, rdf=rdf,
                                          cast_datetime=cast_datetime,
                                          allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                                          warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)
        else:  # must be a dte / kwantWrd
            if attribute_to_set.waarde is None:
                attribute_to_set.add_empty_value()

            if cast_datetime and attribute_to_set.waarde._waarde.field in [TimeField, DateField, DateTimeField]:
                value = attribute_to_set.waarde._waarde.field.convert_to_correct_type(value=value, log_warnings=False)
            attribute_to_set.waarde._waarde.set_waarde(value)
    else:
        if cast_datetime and attribute_to_set.field in [TimeField, DateField, DateTimeField]:
            value = attribute_to_set.field.convert_to_correct_type(value=value, log_warnings=False)
        attribute_to_set.set_waarde(value)


def dynamic_create_type_from_ns_and_name(namespace: str, class_name: str, model_directory: Path = None) -> type:
    """Loads the OTL class module and attempts to return the type using the name and namespace of the class

    :param namespace: namespace of the class
    :type: str
    :param class_name: class name to instantiate
    :type: str
    :param model_directory: directory where the model is located, defaults to otlmow_model's own model
    :type: str
    :return: returns an instance of class_name in the given namespace, located from directory
    :rtype: type
    """
    try:
        class_dict = get_hardcoded_class_dict(model_directory=model_directory)
    except FileNotFoundError as e:
        raise CouldNotCreateInstanceError(
            e.message + '\nMake sure you are directing to the (parent) directory '
            'where OtlmowModel is located in.'
        ) from e
    class_entry = next((c for c in class_dict.values() if c['ns'] == namespace and c['name'] == class_name), None)
    if class_entry is not None:
        return _create_type_from_class_dict_entry(class_entry, model_directory=model_directory)

    error = CouldNotCreateInstanceError(
        f'The combination of the namespace {namespace} and the class name {class_name} is not found in the hardcoded '
        f'class dictionary.')

    ns_match = next((c for c in class_dict.values() if c['ns'] == namespace), None)
    if ns_match is None:
        error.message += f'\nNo classes found with the namespace {namespace}.'
        from difflib import get_close_matches
        closest_matches = get_close_matches(namespace, {c['ns'] for c in class_dict.values()}, n=5, cutoff=0.8)
        closest_matches_string = '", "'.join(closest_matches)
        error.message += f'\nDid you mean one of these namespaces? "{closest_matches_string}"'
        raise error

    from difflib import get_close_matches
    closest_matches = get_close_matches(class_name, {c['name'] for c in class_dict.values()}, n=5, cutoff=0.8)
    closest_matches_string = '", "'.join(closest_matches)

    error.message += (f'\nNo classes found with the namespace {namespace}.'
                      f'nDid you mean one of these class names? "{closest_matches_string}"')
    error.closest_matches = closest_matches
    raise error





def dynamic_create_instance_from_ns_and_name(namespace: str, class_name: str, model_directory: Path = None) -> OTLObject:
    """Loads the OTL class module and attempts to instantiate the class using the name and namespace of the class.
    Caches imported modules for performance improvement.

    :param namespace: namespace of the class
    :type: str
    :param class_name: class name to instantiate
    :type: str
    :param model_directory: directory where the model is located, defaults to otlmow_model's own model
    :type: Path
    :return: returns an instance of class_name in the given namespace, located from directory
    :rtype: OTLObject
    """
    type_ = dynamic_create_type_from_ns_and_name(namespace=namespace, class_name=class_name,
                                                 model_directory=model_directory)
    return type_()


def dynamic_create_instance_from_uri(class_uri: str, model_directory: Path = None) -> OTLObject:
    """Loads the OTL class module and attempts to instantiate the class using the URI of the class.

    :param class_uri: URI of the class
    :type: str
    :param model_directory: directory where the model is located, defaults to otlmow_model's own model
    :type: Path
    :return: returns an instance of the class with the given URI, located from directory
    :rtype: OTLObject
    """
    type_ = dynamic_create_type_from_uri(class_uri, model_directory=model_directory)
    return type_()


def dynamic_create_type_from_uri(class_uri: str, model_directory: Path = None) -> type:
    """Loads the OTL class module and attempts to return the type using the URI of the class.

    :param class_uri: URI of the class
    :type: str
    :param model_directory: directory where the model is located, defaults to otlmow_model's own model
    :type: Path
    :return: returns a type object created from the class URI
    :rtype: type
    """
    try:
        class_dict = get_hardcoded_class_dict(model_directory=model_directory)
    except FileNotFoundError as e:
        raise CouldNotCreateInstanceError(
            e.message + '\nMake sure you are directing to the (parent) directory '
            'where OtlmowModel is located in.'
        ) from e
    if class_uri in class_dict:
        return _create_type_from_class_dict_entry(class_dict[class_uri], model_directory=model_directory)

    from difflib import get_close_matches
    closest_matches = get_close_matches(class_uri, class_dict.keys(), n=5, cutoff=0.8)
    closest_matches_string = '", "'.join(closest_matches)

    error = CouldNotCreateInstanceError(
        f'Class URI {class_uri} is not found in the hardcoded class dictionary. '
        f'Did you mean one of these? "{closest_matches_string}"')
    error.closest_matches = closest_matches
    raise error


_imported_modules = {}

def _create_type_from_class_dict_entry(class_dict_entry: Dict[str, str], model_directory: Path = None) -> type:
    """Creates a type from a class dictionary entry.

    :param class_dict_entry: dictionary containing the class information
    :type class_dict_entry: dict
    :param model_directory: directory where the model is located, defaults to otlmow_model's own model
    :type model_directory: Path
    :return: returns a type object created from the class dictionary entry
    :rtype: type
    """
    global _imported_modules
    namespace = class_dict_entry['ns']
    class_name = class_dict_entry['name']
    module_key = (namespace, class_name)

    if module_key in _imported_modules:
        mod = _imported_modules[module_key]
    else:
        model_directory_given = model_directory is not None
        if model_directory is None:
            current_file_path = Path(__file__)
            model_directory = current_file_path.parent.parent.parent

        namespace_path = '' if namespace == '' else f'{get_titlecase_from_ns(namespace)}.'
        module_path = f'OtlmowModel.Classes.{namespace_path}{class_name}'

        try:
            if str(model_directory) not in sys.path:
                sys.path.insert(1, str(model_directory))
            mod = importlib.import_module(module_path)
            _imported_modules[module_key] = mod
        except ModuleNotFoundError as e:
            error = CouldNotCreateInstanceError(
                f'When dynamically creating an object of class {class_name}, the import failed. ')
            if model_directory_given:
                error.message += 'Make sure you are directing to the (parent) directory where OtlmowModel is located in.'
            raise error from e

    return getattr(mod, class_name)
