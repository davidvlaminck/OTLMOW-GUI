# coding=utf-8
from otlmow_model.OtlmowModel.BaseClasses.ComplexField import ComplexField
from otlmow_model.OtlmowModel.BaseClasses.WaardenObject import WaardenObject
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLAttribuut
from otlmow_model.OtlmowModel.BaseClasses.StringField import StringField


class DteAssetTypeWaarden(WaardenObject):
    def __init__(self):
        WaardenObject.__init__(self)
        self._typeURI = OTLAttribuut(
            field=StringField,
            naam='typeURI',
            label='typeURI',
            objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.typeURI',
            definition='De uri van het assettype.',
            owner=self)

    @property
    def typeURI(self):
        """De uri van het assettype."""
        return self._typeURI.get_waarde()

    @typeURI.setter
    def typeURI(self, value):
        self._typeURI.set_waarde(value, owner=self._parent)


class DteAssetType(ComplexField):
    """Complex datatype om het assettype te benoemen"""
    naam = 'DteAssetType'
    label = 'AssetType'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DteAssetType'
    definition = 'Complex datatype om het assettype te benoemen.'
    waardeObject = DteAssetTypeWaarden

    def __str__(self) -> str:
        return ComplexField.__str__(self)
