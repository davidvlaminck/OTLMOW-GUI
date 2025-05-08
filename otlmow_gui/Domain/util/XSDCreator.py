import asyncio
import xml.etree.cElementTree as ET
from pathlib import Path
from typing import Optional
from xml.etree.ElementTree import Element

from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_model.OtlmowModel.BaseClasses.BooleanField import BooleanField
from otlmow_model.OtlmowModel.BaseClasses.DateField import DateField
from otlmow_model.OtlmowModel.BaseClasses.DateTimeField import DateTimeField
from otlmow_model.OtlmowModel.BaseClasses.FloatOrDecimalField import FloatOrDecimalField
from otlmow_model.OtlmowModel.BaseClasses.IntegerField import IntegerField
from otlmow_model.OtlmowModel.BaseClasses.KeuzelijstField import KeuzelijstField
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import dynamic_create_instance_from_uri, OTLAttribuut, OTLObject
from otlmow_model.OtlmowModel.BaseClasses.StringField import StringField
from otlmow_model.OtlmowModel.BaseClasses.TimeField import TimeField
from otlmow_model.OtlmowModel.BaseClasses.URIField import URIField
from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import is_relation
from otlmow_modelbuilder.OSLOCollector import OSLOCollector

from otlmow_gui.exception_handler.ExceptionHandlers import create_task_reraise_exception


class XSDCreator:

    @classmethod
    def create_xsd_from_subset(cls, subset_path: Path, xsd_path: Path,
                               model_directory: Path = None) -> None:
        create_task_reraise_exception(cls.create_filtered_xsd_from_subset(subset_path=subset_path, xsd_path=xsd_path,
                                            selected_classes_typeURI_list=[], model_directory=model_directory))

    @classmethod
    async def create_filtered_xsd_from_subset(
            cls, subset_path: Path, xsd_path: Path, selected_classes_typeURI_list: Optional[list[str]]=None,
            model_directory: Path = None) -> None:

        collector = OSLOCollector(subset_path)
        collector.collect_all(include_abstract=True)

        ET.register_namespace("xs", 'http://www.w3.org/2001/XMLSchema')
        ET.register_namespace("gml", 'http://www.opengis.net/gml')
        ET.register_namespace("Schema1", 'http://fdo.osgeo.org/schemas/feature/Schema1')
        ET.register_namespace("fdo", 'http://fdo.osgeo.org/schemas')

        schema = ET.Element("{http://www.w3.org/2001/XMLSchema}schema", targetNamespace="http://fdo.osgeo.org/schemas/feature/Schema1",  elementFormDefault="qualified", attributeFormDefault="unqualified" )
        annotation = ET.SubElement(schema, "{http://www.w3.org/2001/XMLSchema}annotation")
        documentation = ET.SubElement(annotation, "{http://www.w3.org/2001/XMLSchema}documentation")
        documentation.text = "Default schema"
        tree = ET.ElementTree(schema)

        if selected_classes_typeURI_list:
            classes = [class_ for class_ in  collector.classes if class_.objectUri in selected_classes_typeURI_list]
        else:
            # if no selected_classes are given take everything from subset
            classes = collector.classes

        for class_ in classes:
            if class_.abstract:
                continue
            class_instance = dynamic_create_instance_from_uri(class_.objectUri, model_directory=model_directory)
            if is_relation(class_instance):
                continue

            class_element = ET.SubElement(
                schema, "{http://www.w3.org/2001/XMLSchema}element",
                attrib={'name': f"OTL_{class_.name}",
                        'type': f"http://fdo.osgeo.org/schemas/feature/Schema1/OTL_{class_.name}Type",
                        'abstract': "false", 'substitutionGroup': "http://www.opengis.net/gml/_Feature"})
            key = ET.SubElement(class_element, "{http://www.w3.org/2001/XMLSchema}key", name=f"OTL_{class_.name}Key")
            ET.SubElement(key, "{http://www.w3.org/2001/XMLSchema}selector", xpath=f".//OTL_{class_.name}")
            ET.SubElement(key, "{http://www.w3.org/2001/XMLSchema}field", xpath="FeatId")



            complex_type = ET.SubElement(schema, "{http://www.w3.org/2001/XMLSchema}complexType",
                                         attrib={'name': f"OTL_{class_.name}Type", 'abstract': "false",
                                                 '{http://fdo.osgeo.org/schemas}geometryName': "Geometry"})
            annotation = ET.SubElement(complex_type, "{http://www.w3.org/2001/XMLSchema}annotation")
            documentation = ET.SubElement(annotation, "{http://www.w3.org/2001/XMLSchema}documentation")
            documentation.text = class_instance.__doc__
            if documentation.text is not None:
                documentation.text = documentation.text[:159]
            complex_content = ET.SubElement(complex_type, "{http://www.w3.org/2001/XMLSchema}complexContent")
            extension = ET.SubElement(complex_content, "{http://www.w3.org/2001/XMLSchema}extension",
                                      attrib={'base': "http://www.opengis.net/gml/AbstractFeatureType"})
            attribute_sequence = ET.SubElement(extension, "{http://www.w3.org/2001/XMLSchema}sequence")

            cls.add_feat_id_in_attribute_sequence(attribute_sequence)

            cls.add_geometry_in_attribute_sequence(attribute_sequence, class_instance)

            attribute_names_in_subset = [attribuut.name for attribuut in collector.find_attributes_by_class(class_)]

            if 'geometry' in attribute_names_in_subset:
                attribute_names_in_subset.remove('geometry')
            class_instance.fill_with_dummy_data()
            DotnotationHelper.clear_list_of_list_attributes(class_instance)

            cls.add_otl_attributes_in_attribute_sequence(attribute_names_in_subset, attribute_sequence, class_instance)
            await asyncio.sleep(0)

        tree.write(xsd_path, encoding='utf-8', xml_declaration=True, method='xml')

        cls._tweak_file(xsd_path)

    @classmethod
    def add_geometry_in_attribute_sequence(cls, attribute_sequence: Element, class_instance: OTLObject) -> None:
        if not hasattr(class_instance, '_geometry_types'):
            geo_types = ""
        else:
            geo_types = ' '.join(class_instance._geometry_types).replace(' Z', '').lower()
            if geo_types != '':
                geo_types += ' '

        geometry = ET.SubElement(
            attribute_sequence, "{http://www.w3.org/2001/XMLSchema}element",
            attrib={'name': "Geometry", 'type': "http://www.opengis.net/gml/AbstractGeometryType",
                    '{http://fdo.osgeo.org/schemas}hasMeasure': "false",
                    '{http://fdo.osgeo.org/schemas}hasElevation': "true",
                    '{http://fdo.osgeo.org/schemas}srsName': "Default",
                    '{http://fdo.osgeo.org/schemas}geometricTypes': geo_types,
                    '{http://fdo.osgeo.org/schemas}geometryTypes': geo_types}
        )
        annotation = ET.SubElement(geometry, "{http://www.w3.org/2001/XMLSchema}annotation")
        documentation = ET.SubElement(annotation, "{http://www.w3.org/2001/XMLSchema}documentation")
        documentation.text = "Default geometry property"

    @classmethod
    def add_feat_id_in_attribute_sequence(cls, attribute_sequence: Element):
        feat_id = ET.SubElement(attribute_sequence, "{http://www.w3.org/2001/XMLSchema}element",
                                attrib={'name': "FeatId", '{http://fdo.osgeo.org/schemas}readOnly': "true",
                                        '{http://fdo.osgeo.org/schemas}autogenerated': "true"})
        annotation = ET.SubElement(feat_id, "{http://www.w3.org/2001/XMLSchema}annotation")
        documentation = ET.SubElement(annotation, "{http://www.w3.org/2001/XMLSchema}documentation")
        documentation.text = "Default identity property"
        simple_type = ET.SubElement(feat_id, "{http://www.w3.org/2001/XMLSchema}simpleType")
        ET.SubElement(simple_type, "{http://www.w3.org/2001/XMLSchema}restriction", base="xs:int")

    @classmethod
    def add_otl_attributes_in_attribute_sequence(cls, attribute_names_in_subset: [str], attribute_sequence: Element,
                                                 class_instance: OTLObject) -> None:
        for dotnotation, _ in DotnotationHelper.list_attributes_and_values_by_dotnotation(
                class_instance, waarde_shortcut=True):
            first_in_dotnotation = dotnotation
            if '.' in first_in_dotnotation:
                first_in_dotnotation = first_in_dotnotation.split('.')[0]
            if '[]' in first_in_dotnotation:
                first_in_dotnotation = first_in_dotnotation[:-2]
            if first_in_dotnotation not in attribute_names_in_subset:
                continue

            attr_instance = DotnotationHelper.get_attribute_by_dotnotation(class_instance, dotnotation)
            definition = attr_instance.definition
            if hasattr(attr_instance.owner, '_parent'):
                parent_attribute_for_waarde_shortcut = attr_instance.owner._parent
                if parent_attribute_for_waarde_shortcut.field.waarde_shortcut_applicable:
                    dotnotation = DotnotationHelper.get_dotnotation(parent_attribute_for_waarde_shortcut)
                    definition = parent_attribute_for_waarde_shortcut.definition

            element = ET.SubElement(attribute_sequence, "{http://www.w3.org/2001/XMLSchema}element",
                                    name=dotnotation.replace('.', '_'), minOccurs="0", default="")
            annotation = ET.SubElement(element, "{http://www.w3.org/2001/XMLSchema}annotation")
            documentation = ET.SubElement(annotation, "{http://www.w3.org/2001/XMLSchema}documentation")
            documentation.text = definition
            if documentation.text is not None:
                documentation.text = documentation.text[:159]

            cls.create_type_from_attribute_in_element(element, attr_instance)

        # hard add typeURI
        element = ET.SubElement(attribute_sequence, "{http://www.w3.org/2001/XMLSchema}element",
                                name='typeURI', minOccurs="0", default=class_instance.typeURI)
        annotation = ET.SubElement(element, "{http://www.w3.org/2001/XMLSchema}annotation")
        documentation = ET.SubElement(annotation, "{http://www.w3.org/2001/XMLSchema}documentation")
        documentation.text = 'De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI.'
        simple_type = ET.SubElement(element, "{http://www.w3.org/2001/XMLSchema}simpleType")
        restriction = ET.SubElement(simple_type, "{http://www.w3.org/2001/XMLSchema}restriction", base="xs:string")
        ET.SubElement(restriction, "{http://www.w3.org/2001/XMLSchema}maxLength", value="9999")

    @classmethod
    def _tweak_file(cls, xsd_path):
        # open file
        with open(xsd_path, 'r') as file:
            data = file.readlines()

        new_data = []
        for line in data:
            line = line.replace('>', '>\n')
            new_data.extend(line.split('\n'))

        # tweak file
        if new_data[3][:10] == '<xs:schema':
            new_data[3] = ('<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" targetNamespace="http://fdo.osgeo.org/schemas/feature/Schema1" '
                           'xmlns:fdo="http://fdo.osgeo.org/schemas" xmlns:gml="http://www.opengis.net/gml" '
                           'xmlns:Schema1="http://fdo.osgeo.org/schemas/feature/Schema1" elementFormDefault="qualified" '
                           'attributeFormDefault="unqualified">')

        for index, line in enumerate(new_data):
            if line.startswith('<xs:element name='):
                new_data[index] = line.replace('http://fdo.osgeo.org/schemas/feature/Schema1/', 'Schema1:').replace('http://www.opengis.net/gml/', 'gml:')
            elif line.startswith('<xs:extension base="http://www.opengis.net/gml/AbstractFeatureType">'):
                new_data[index] = '<xs:extension base="gml:AbstractFeatureType">'

        # write file
        with open(xsd_path, 'w') as file:
            file.writelines(new_data)

    @classmethod
    def create_type_from_attribute_in_element(cls, element: Element, attr_instance: OTLAttribuut):
        if attr_instance.field == FloatOrDecimalField:
            simple_type = ET.SubElement(element, "{http://www.w3.org/2001/XMLSchema}simpleType")
            restriction = ET.SubElement(simple_type, "{http://www.w3.org/2001/XMLSchema}restriction", base="xs:decimal")
            ET.SubElement(restriction, "{http://www.w3.org/2001/XMLSchema}totalDigits", value="19")
            ET.SubElement(restriction, "{http://www.w3.org/2001/XMLSchema}fractionDigits", value="10")
        elif attr_instance.field == BooleanField:
            simple_type = ET.SubElement(element, "{http://www.w3.org/2001/XMLSchema}simpleType")
            ET.SubElement(simple_type, "{http://www.w3.org/2001/XMLSchema}restriction", base="xs:boolean")
        elif attr_instance.field in {StringField, DateField, DateTimeField, TimeField, URIField} or attr_instance.field.objectUri == 'http://www.w3.org/2001/XMLSchema#string':
            simple_type = ET.SubElement(element, "{http://www.w3.org/2001/XMLSchema}simpleType")
            restriction = ET.SubElement(simple_type, "{http://www.w3.org/2001/XMLSchema}restriction", base="xs:string")
            ET.SubElement(restriction, "{http://www.w3.org/2001/XMLSchema}maxLength", value="9999")
        elif issubclass(attr_instance.field, KeuzelijstField):
            simple_type = ET.SubElement(element, "{http://www.w3.org/2001/XMLSchema}simpleType")
            restriction = ET.SubElement(simple_type, "{http://www.w3.org/2001/XMLSchema}restriction", base="xs:string")
            ET.SubElement(restriction, "{http://www.w3.org/2001/XMLSchema}enumeration", value='-')
            element.attrib.update({'default': '-'})
            max_length = 50
            for keuze, keuzelijstwaarde in attr_instance.field.options.items():
                if keuzelijstwaarde.status != 'ingebruik':
                    continue
                ET.SubElement(restriction, "{http://www.w3.org/2001/XMLSchema}enumeration", value=keuze)
                max_length = max(max_length, len(keuze))
            ET.SubElement(restriction, "{http://www.w3.org/2001/XMLSchema}maxLength", value=str(max_length))
        elif issubclass(attr_instance.field, IntegerField):
            simple_type = ET.SubElement(element, "{http://www.w3.org/2001/XMLSchema}simpleType")
            restriction = ET.SubElement(simple_type, "{http://www.w3.org/2001/XMLSchema}restriction", base="xs:int")
        else:
            raise NotImplementedError(f"Field {attr_instance.field} not implemented")
