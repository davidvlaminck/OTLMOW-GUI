# coding=utf-8
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLAttribuut
from otlmow_model.OtlmowModel.BaseClasses.WaardenObject import WaardenObject
from otlmow_model.OtlmowModel.BaseClasses.ComplexField import ComplexField
from ..Datatypes.KwantWrdTest import KwantWrdTest, KwantWrdTestWaarden
from otlmow_model.OtlmowModel.BaseClasses.StringField import StringField


# Generated with OTLComplexDatatypeCreator. To modify: extend, do not edit
class DtcTestComplexType2Waarden(WaardenObject):
    def __init__(self):
        WaardenObject.__init__(self)
        self._testKwantWrd = OTLAttribuut(field=KwantWrdTest,
                                          naam='testKwantWrd',
                                          label='Test kwantitatieve waarde',
                                          objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType2.testKwantWrd',
                                          definition='Test attribuut voor Kwantitatieve waarde in een complex datatype.',
                                          owner=self)

        self._testStringField = OTLAttribuut(field=StringField,
                                             naam='testStringField',
                                             label='Test tekstveld',
                                             objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType2.testStringField',
                                             definition='Test attribuut voor tekst in een complex datatype.',
                                             owner=self)

    @property
    def testKwantWrd(self) -> KwantWrdTestWaarden:
        """Test attribuut voor Kwantitatieve waarde in een complex datatype."""
        return self._testKwantWrd.get_waarde()

    @testKwantWrd.setter
    def testKwantWrd(self, value):
        self._testKwantWrd.set_waarde(value, owner=self._parent)

    @property
    def testStringField(self) -> str:
        """Test attribuut voor tekst in een complex datatype."""
        return self._testStringField.get_waarde()

    @testStringField.setter
    def testStringField(self, value):
        self._testStringField.set_waarde(value, owner=self._parent)


# Generated with OTLComplexDatatypeCreator. To modify: extend, do not edit
class DtcTestComplexType2(ComplexField):
    """Test datatype voor een complexe waarde in een complexe waarde"""
    naam = 'DtcTestComplexType2'
    label = 'Test ComplexType2'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType2'
    definition = 'Test datatype voor een complexe waarde in een complexe waarde'
    waardeObject = DtcTestComplexType2Waarden

    def __str__(self):
        return ComplexField.__str__(self)

