# coding=utf-8
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLAttribuut
from ...Classes.ImplementatieElement.AIMObject import AIMObject
from otlmow_model.OtlmowModel.BaseClasses.StringField import StringField
from otlmow_model.OtlmowModel.GeometrieTypes.LijnGeometrie import LijnGeometrie


# Generated with OTLClassCreator. To modify: extend, do not edit
class AnotherTestClass(AIMObject, LijnGeometrie):
    """Just another TestClass to test relations"""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    def __init__(self):
        super().__init__()

        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', target='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', direction='u')  # u = unidirectional
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Voedt', target='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AllCasesTestClass', direction='i', deprecated='2.0')  # i = direction: incoming

        self._deprecatedString = OTLAttribuut(field=StringField,
                                              naam='deprecatedString',
                                              label='Deprecated Tekstveld',
                                              objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AnotherTestClass.deprecatedString',
                                              deprecated_version='2.0.0',
                                              constraints=' ',
                                              definition='Tekstveld dat niet meer gebruikt wordt',
                                              owner=self)

    @property
    def deprecatedString(self) -> str:
        """Tekstveld dat niet meer gebruikt wordt"""
        return self._deprecatedString.get_waarde()

    @deprecatedString.setter
    def deprecatedString(self, value):
        self._deprecatedString.set_waarde(value, owner=self)
