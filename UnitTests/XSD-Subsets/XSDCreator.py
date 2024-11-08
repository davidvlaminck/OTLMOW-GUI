from pathlib import Path
import xml.etree.cElementTree as ET

from otlmow_converter.DotnotationHelper import DotnotationHelper
from otlmow_model.OtlmowModel.BaseClasses.BooleanField import BooleanField
from otlmow_model.OtlmowModel.BaseClasses.DateField import DateField
from otlmow_model.OtlmowModel.BaseClasses.DateTimeField import DateTimeField
from otlmow_model.OtlmowModel.BaseClasses.FloatOrDecimalField import FloatOrDecimalField
from otlmow_model.OtlmowModel.BaseClasses.KeuzelijstField import KeuzelijstField
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import dynamic_create_type_from_uri, get_attribute_by_name, \
    get_attribute_by_uri, dynamic_create_instance_from_uri
from otlmow_model.OtlmowModel.BaseClasses.StringField import StringField
from otlmow_model.OtlmowModel.BaseClasses.TimeField import TimeField
from otlmow_modelbuilder.OSLOCollector import OSLOCollector


def create_type_from_attribute_in_element(element, attr_instance):
    if attr_instance.field == FloatOrDecimalField:
        simple_type = ET.SubElement(element, "{http://www.w3.org/2001/XMLSchema}simpleType")
        restriction = ET.SubElement(simple_type, "{http://www.w3.org/2001/XMLSchema}restriction", base="xs:decimal")
        total_digits = ET.SubElement(restriction, "{http://www.w3.org/2001/XMLSchema}totalDigits", value="19")
        fraction_digits = ET.SubElement(restriction, "{http://www.w3.org/2001/XMLSchema}fractionDigits", value="10")
    elif attr_instance.field == BooleanField:
        simple_type = ET.SubElement(element, "{http://www.w3.org/2001/XMLSchema}simpleType")
        restriction = ET.SubElement(simple_type, "{http://www.w3.org/2001/XMLSchema}restriction", base="xs:boolean")
    elif attr_instance.field in {StringField, DateField, DateTimeField, TimeField}:
        simple_type = ET.SubElement(element, "{http://www.w3.org/2001/XMLSchema}simpleType")
        restriction = ET.SubElement(simple_type, "{http://www.w3.org/2001/XMLSchema}restriction", base="xs:string")
        max_length = ET.SubElement(restriction, "{http://www.w3.org/2001/XMLSchema}maxLength", value="9999")
    elif issubclass(attr_instance.field, KeuzelijstField):
        simple_type = ET.SubElement(element, "{http://www.w3.org/2001/XMLSchema}simpleType")
        restriction = ET.SubElement(simple_type, "{http://www.w3.org/2001/XMLSchema}restriction", base="xs:string")
        element.attrib.update({'default': '-'})
        max_length = 1
        for keuze, keuzelijstwaarde in attr_instance.field.options.items():
            if keuzelijstwaarde.status != 'ingebruik':
                continue
            enumeration = ET.SubElement(restriction, "{http://www.w3.org/2001/XMLSchema}enumeration", value=keuze)
            max_length = max(max_length, len(keuze))
        max_length = ET.SubElement(restriction, "{http://www.w3.org/2001/XMLSchema}maxLength", value=str(max_length))

class XSDCreator:
    @classmethod
    def create_xsd_from_subset(cls, subset_path, xsd_path):
        collector = OSLOCollector(subset_path)
        collector.collect_all(include_abstract=True)

        import xml.etree.cElementTree as ET

        schema = ET.Element("{http://www.w3.org/2001/XMLSchema}schema", targetNamespace="http://fdo.osgeo.org/schemas/feature/Schema1",  elementFormDefault="qualified", attributeFormDefault="unqualified" )
        annotation = ET.SubElement(schema, "{http://www.w3.org/2001/XMLSchema}annotation")
        documentation = ET.SubElement(annotation, "{http://www.w3.org/2001/XMLSchema}documentation")
        documentation.text = "Default schema"

        tree = ET.ElementTree(schema)
        tree.write("filename.xml")

        ET.register_namespace("xs", 'http://www.w3.org/2001/XMLSchema')
        ET.register_namespace("gml", 'http://www.opengis.net/gml')
        #ET.register_namespace("Schema1", 'http://fdo.osgeo.org/schemas/feature/Schema1')
        ET.register_namespace("fdo", 'http://fdo.osgeo.org/schemas')

        classes = collector.classes
        for class_ in classes:
            if class_.abstract:
                continue
            class_element = ET.SubElement(
                schema, "{http://www.w3.org/2001/XMLSchema}element",
                attrib={'name': f"OTL_{class_.name}", 'type': f"{{http://fdo.osgeo.org/schemas/feature/Schema1}}OTL_{class_.name}Type",
                        'abstract': "false", 'substitutionGroup': "{http://www.opengis.net/gml}_Feature"}
            )
            key = ET.SubElement(class_element, "{http://www.w3.org/2001/XMLSchema}key", name=f"OTL_{class_.name}Key")
            selector = ET.SubElement(key, "{http://www.w3.org/2001/XMLSchema}selector", xpath=f".//OTL_{class_.name}")
            field = ET.SubElement(key, "{http://www.w3.org/2001/XMLSchema}field", xpath="FeatId")

            class_instance = dynamic_create_instance_from_uri(class_.objectUri)

            complex_type = ET.SubElement(schema, "{http://www.w3.org/2001/XMLSchema}complexType",
                                         attrib={'name': f"OTL_{class_.name}Type", 'abstract': "false",
                                                 '{http://fdo.osgeo.org/schemas}geometryName': "Geometry"})
            annotation = ET.SubElement(complex_type, "{http://www.w3.org/2001/XMLSchema}annotation")
            documentation = ET.SubElement(annotation, "{http://www.w3.org/2001/XMLSchema}documentation")
            documentation.text = class_instance.__doc__
            complex_content = ET.SubElement(complex_type, "{http://www.w3.org/2001/XMLSchema}complexContent")
            extension = ET.SubElement(complex_content, "{http://www.w3.org/2001/XMLSchema}extension",
                                      attrib={'base': "{http://www.opengis.net/gml}AbstractFeatureType"})
            attribute_sequence = ET.SubElement(extension, "{http://www.w3.org/2001/XMLSchema}sequence")


            feat_id = ET.SubElement(attribute_sequence, "{http://www.w3.org/2001/XMLSchema}element", name="FeatId", readOnly="true", autogenerated="true")
            annotation = ET.SubElement(feat_id, "{http://www.w3.org/2001/XMLSchema}annotation")
            documentation = ET.SubElement(annotation, "{http://www.w3.org/2001/XMLSchema}documentation")
            documentation.text = "Default identity property"
            simple_type = ET.SubElement(feat_id, "{http://www.w3.org/2001/XMLSchema}simpleType")
            restriction = ET.SubElement(simple_type, "{http://www.w3.org/2001/XMLSchema}restriction", base="xs:int")

            # TODO use _geometry_types
            geo_types = ' '.join(class_instance._geometry_types).replace(' Z', '').lower()
            geometry = ET.SubElement(
                attribute_sequence, "{http://www.w3.org/2001/XMLSchema}element",
                attrib= {'name': "Geometry", 'type': "{http://www.opengis.net/gml}AbstractGeometryType", '{http://fdo.osgeo.org/schemas}hasMeasure': "false", '{http://fdo.osgeo.org/schemas}hasElevation': "true", '{http://fdo.osgeo.org/schemas}srsName': "Default", '{http://fdo.osgeo.org/schemas}geometricTypes': geo_types, '{http://fdo.osgeo.org/schemas}geometryTypes': geo_types}
            )
            annotation = ET.SubElement(geometry, "{http://www.w3.org/2001/XMLSchema}annotation")
            documentation = ET.SubElement(annotation, "{http://www.w3.org/2001/XMLSchema}documentation")
            documentation.text = "Default geometry property"

            attribute_names_of_subset = [attribuut.name for attribuut in collector.find_attributes_by_class(class_)]
            class_instance.fill_with_dummy_data()

            for dotnotation, _ in DotnotationHelper.list_attributes_and_values_by_dotnotation(class_instance, waarde_shortcut=True):
                first_in_dotnotation = dotnotation
                if '.' in first_in_dotnotation:
                    first_in_dotnotation = first_in_dotnotation.split('.')[0]
                if '[]' in first_in_dotnotation:
                    first_in_dotnotation = first_in_dotnotation[:-2]
                if first_in_dotnotation not in attribute_names_of_subset:
                    continue

                attr_instance = DotnotationHelper.get_attribute_by_dotnotation(class_instance, dotnotation)
                definition = attr_instance.definition
                if hasattr(attr_instance.owner, '_parent'):
                    o = attr_instance.owner._parent
                    if o.field.waarde_shortcut_applicable:
                        dotnotation = DotnotationHelper.get_dotnotation(o)
                        definition = o.definition

                print(attr_instance.naam, attr_instance.field.naam)


                element = ET.SubElement(attribute_sequence, "{http://www.w3.org/2001/XMLSchema}element", name=dotnotation.replace('.', '_'), minOccurs="0", default="")
                annotation = ET.SubElement(element, "{http://www.w3.org/2001/XMLSchema}annotation")
                documentation = ET.SubElement(annotation, "{http://www.w3.org/2001/XMLSchema}documentation")
                documentation.text = definition

                simple_type = create_type_from_attribute_in_element(element, attr_instance)

        tree.write(xsd_path, encoding='utf-8', xml_declaration=True, method='xml')

def test_create_xsd_from_subset():
    kast_path = Path(__file__).parent / 'subset_wegkantkast.db'
    created_path = Path(__file__).parent / 'created_wegkantkast.xsd'

    XSDCreator.create_xsd_from_subset(kast_path, created_path)

    result = ET.tostring(ET.parse(created_path).getroot())
    expected = ET.tostring(ET.parse(Path(__file__).parent / 'xsd_export_wegkantkast.xsd').getroot())

    assert expected == result