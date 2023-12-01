# coding=utf-8
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLAttribuut
from otlmow_model.OtlmowModel.BaseClasses.WaardenObject import WaardenObject
from otlmow_model.OtlmowModel.BaseClasses.ComplexField import ComplexField
from otlmow_model.OtlmowModel.BaseClasses.StringField import StringField


# Generated with OTLComplexDatatypeCreator. To modify: extend, do not edit
class DtcIdentificatorWaarden(WaardenObject):
    def __init__(self):
        WaardenObject.__init__(self)
        self._identificator = OTLAttribuut(field=StringField,
                                           naam='identificator',
                                           label='identificator',
                                           objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcIdentificator.identificator',
                                           definition='Een groep van tekens om een AIM object te identificeren of te benoemen.',
                                           owner=self)

        self._toegekendDoor = OTLAttribuut(field=StringField,
                                           naam='toegekendDoor',
                                           label='toegekend door',
                                           objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcIdentificator.toegekendDoor',
                                           definition='Gegevens van de organisatie die de toekenning deed.',
                                           owner=self)

    @property
    def identificator(self) -> str:
        """Een groep van tekens om een AIM object te identificeren of te benoemen."""
        return self._identificator.get_waarde()

    @identificator.setter
    def identificator(self, value):
        self._identificator.set_waarde(value, owner=self._parent)

    @property
    def toegekendDoor(self) -> str:
        """Gegevens van de organisatie die de toekenning deed."""
        return self._toegekendDoor.get_waarde()

    @toegekendDoor.setter
    def toegekendDoor(self, value):
        self._toegekendDoor.set_waarde(value, owner=self._parent)


# Generated with OTLComplexDatatypeCreator. To modify: extend, do not edit
class DtcIdentificator(ComplexField):
    """Complex datatype voor de identificator van een AIM object volgens de bron van de identificator."""
    naam = 'DtcIdentificator'
    label = 'Identificator'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcIdentificator'
    definition = 'Complex datatype voor de identificator van een AIM object volgens de bron van de identificator.'
    waardeObject = DtcIdentificatorWaarden

    def __str__(self):
        return ComplexField.__str__(self)

