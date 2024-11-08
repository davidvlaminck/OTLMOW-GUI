# coding=utf-8
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLAttribuut
from otlmow_model.OtlmowModel.BaseClasses.OTLField import OTLField
from otlmow_model.OtlmowModel.BaseClasses.WaardenObject import WaardenObject
from otlmow_model.OtlmowModel.BaseClasses.NonNegIntegerField import NonNegIntegerField
from otlmow_model.OtlmowModel.BaseClasses.StringField import StringField


# Generated with OTLPrimitiveDatatypeCreator. To modify: extend, do not edit
class KwantWrdInMaandWaarden(WaardenObject):
    def __init__(self):
        WaardenObject.__init__(self)
        self._standaardEenheid = OTLAttribuut(field=StringField,
                                              naam='standaardEenheid',
                                              label='standaard eenheid',
                                              objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#KwantWrdInMaand.standaardEenheid',
                                              usagenote='"mo"^^cdt:ucumunit',
                                              readonly=True,
                                              constraints='"mo"^^cdt:ucumunit',
                                              definition='De standaard eenheid bij dit datatype is uitgedrukt in maand.',
                                              owner=self)

        self._waarde = OTLAttribuut(field=NonNegIntegerField,
                                    naam='waarde',
                                    label='waarde',
                                    objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#KwantWrdInMaand.waarde',
                                    definition='Bevat een getal die bij het datatype hoort.',
                                    owner=self)

    @property
    def standaardEenheid(self) -> str:
        """De standaard eenheid bij dit datatype is uitgedrukt in maand."""
        return self._standaardEenheid.usagenote.split('"')[1]

    @property
    def waarde(self) -> int:
        """Bevat een getal die bij het datatype hoort."""
        return self._waarde.get_waarde()

    @waarde.setter
    def waarde(self, value):
        self._waarde.set_waarde(value, owner=self._parent)


# Generated with OTLPrimitiveDatatypeCreator. To modify: extend, do not edit
class KwantWrdInMaand(OTLField):
    """Een kwantitatieve waarde die een getal in aantal maanden uitdrukt."""
    naam = 'KwantWrdInMaand'
    label = 'Kwantitatieve waarde in maand'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#KwantWrdInMaand'
    definition = 'Een kwantitatieve waarde die een getal in aantal maanden uitdrukt.'
    waarde_shortcut_applicable = True
    waardeObject = KwantWrdInMaandWaarden

    def __str__(self):
        return OTLField.__str__(self)

