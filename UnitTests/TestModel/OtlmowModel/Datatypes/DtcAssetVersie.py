# coding=utf-8
from datetime import datetime
from ..BaseClasses.OTLObject import OTLAttribuut
from ..BaseClasses.WaardenObject import WaardenObject
from ..BaseClasses.ComplexField import ComplexField
from ..BaseClasses.DateTimeField import DateTimeField
from ..BaseClasses.NonNegIntegerField import NonNegIntegerField
from ..BaseClasses.StringField import StringField


# Generated with OTLComplexDatatypeCreator. To modify: extend, do not edit
class DtcAssetVersieWaarden(WaardenObject):
    def __init__(self):
        WaardenObject.__init__(self)
        self._context = OTLAttribuut(field=StringField,
                                     naam='context',
                                     label='context',
                                     objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcAssetVersie.context',
                                     definition='De context van de versie creatie.',
                                     owner=self)

        self._timestamp = OTLAttribuut(field=DateTimeField,
                                       naam='timestamp',
                                       label='timestamp',
                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcAssetVersie.timestamp',
                                       definition='De timestamp van het moment dat de versienummer werd toegekend.',
                                       owner=self)

        self._versienummer = OTLAttribuut(field=NonNegIntegerField,
                                          naam='versienummer',
                                          label='versienummer',
                                          objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcAssetVersie.versienummer',
                                          definition='Het versienummer als een oplopende integer.',
                                          owner=self)

    @property
    def context(self) -> str:
        """De context van de versie creatie."""
        return self._context.get_waarde()

    @context.setter
    def context(self, value):
        self._context.set_waarde(value, owner=self._parent)

    @property
    def timestamp(self) -> datetime:
        """De timestamp van het moment dat de versienummer werd toegekend."""
        return self._timestamp.get_waarde()

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp.set_waarde(value, owner=self._parent)

    @property
    def versienummer(self) -> int:
        """Het versienummer als een oplopende integer."""
        return self._versienummer.get_waarde()

    @versienummer.setter
    def versienummer(self, value):
        self._versienummer.set_waarde(value, owner=self._parent)


# Generated with OTLComplexDatatypeCreator. To modify: extend, do not edit
class DtcAssetVersie(ComplexField):
    """Complex datatype voor de eigenschappen ten behoeve van de versionering van een asset in de databank."""
    naam = 'DtcAssetVersie'
    label = 'Asset versie'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtcAssetVersie'
    definition = 'Complex datatype voor de eigenschappen ten behoeve van de versionering van een asset in de databank.'
    waardeObject = DtcAssetVersieWaarden

    def __str__(self):
        return ComplexField.__str__(self)

