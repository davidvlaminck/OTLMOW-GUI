# coding=utf-8
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLAttribuut
from otlmow_model.OtlmowModel.BaseClasses.WaardenObject import WaardenObject
from otlmow_model.OtlmowModel.BaseClasses.BooleanField import BooleanField
from otlmow_model.OtlmowModel.BaseClasses.ComplexField import ComplexField
from ..Datatypes.DtcTestComplexType2 import DtcTestComplexType2, DtcTestComplexType2Waarden
from ..Datatypes.KwantWrdTest import KwantWrdTest, KwantWrdTestWaarden
from otlmow_model.OtlmowModel.BaseClasses.StringField import StringField


# Generated with OTLComplexDatatypeCreator. To modify: extend, do not edit
class DtcTestComplexTypeWaarden(WaardenObject):
    def __init__(self):
        WaardenObject.__init__(self)
        self._testBooleanField = OTLAttribuut(field=BooleanField,
                                              naam='testBooleanField',
                                              label='Test boolean veld',
                                              objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testBooleanField',
                                              definition='Test attribuut voor boolean in een complex datatype.',
                                              owner=self)

        self._testComplexType2 = OTLAttribuut(field=DtcTestComplexType2,
                                              naam='testComplexType2',
                                              label='Test complexe waarde',
                                              objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testComplexType2',
                                              definition='Test attribuut voor complexe waarde in een complex datatype.',
                                              owner=self)

        self._testKwantWrd = OTLAttribuut(field=KwantWrdTest,
                                          naam='testKwantWrd',
                                          label='Test kwantitatieve waarde',
                                          objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testKwantWrd',
                                          definition='Test attribuut voor Kwantitatieve waarde in een complex datatype.',
                                          owner=self)

        self._testStringField = OTLAttribuut(field=StringField,
                                             naam='testStringField',
                                             label='Test tekstveld',
                                             objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType.testStringField',
                                             definition='Test attribuut voor tekst in een complex datatype.',
                                             owner=self)

    @property
    def testBooleanField(self) -> bool:
        """Test attribuut voor boolean in een complex datatype."""
        return self._testBooleanField.get_waarde()

    @testBooleanField.setter
    def testBooleanField(self, value):
        self._testBooleanField.set_waarde(value, owner=self._parent)

    @property
    def testComplexType2(self) -> DtcTestComplexType2Waarden:
        """Test attribuut voor complexe waarde in een complex datatype."""
        return self._testComplexType2.get_waarde()

    @testComplexType2.setter
    def testComplexType2(self, value):
        self._testComplexType2.set_waarde(value, owner=self._parent)

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
class DtcTestComplexType(ComplexField):
    """Test datatype voor een complexe waarde"""
    naam = 'DtcTestComplexType'
    label = 'Test ComplexType'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcTestComplexType'
    definition = 'Test datatype voor een complexe waarde'
    waardeObject = DtcTestComplexTypeWaarden

    def __str__(self):
        return ComplexField.__str__(self)

