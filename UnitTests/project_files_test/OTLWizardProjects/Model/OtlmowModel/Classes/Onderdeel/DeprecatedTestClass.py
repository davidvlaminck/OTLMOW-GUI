# coding=utf-8
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject
from otlmow_model.GeometrieTypes.VlakGeometrie import VlakGeometrie


# Generated with OTLClassCreator. To modify: extend, do not edit
class DeprecatedTestClass(AIMObject, VlakGeometrie):
    """Deprecated TestClass"""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#DeprecatedTestClass'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    deprecated_version = '2.0.0'

    def __init__(self):
        super().__init__()
