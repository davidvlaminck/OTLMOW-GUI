# coding=utf-8
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLAttribuut
from abc import abstractmethod
from ...Classes.ImplementatieElement.AIMDBStatus import AIMDBStatus
from otlmow_model.OtlmowModel.BaseClasses.DavieRelatieAttributes import DavieRelatieAttributes
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from ...Datatypes.DtcIdentificator import DtcIdentificator, DtcIdentificatorWaarden


# Generated with OTLClassCreator. To modify: extend, do not edit
class RelatieObject(AIMDBStatus, DavieRelatieAttributes, OTLObject):
    """Abstracte die de relaties voorziet van gemeenschappelijk eigenschappen."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#RelatieObject'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    @abstractmethod
    def __init__(self):
        super().__init__()

        self._assetId = OTLAttribuut(field=DtcIdentificator,
                                     naam='assetId',
                                     label='asset-id',
                                     objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#RelatieObject.assetId',
                                     definition='Unieke identificatie van de asset zoals toegekend door de assetbeheerder of n.a.v. eerste aanlevering door de leverancier.',
                                     owner=self)

        self._bronAssetId = OTLAttribuut(field=DtcIdentificator,
                                         naam='bronAssetId',
                                         label='asset-id bron-asset',
                                         objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#RelatieObject.bronAssetId',
                                         definition='De identificator van het object waaruit de relatie vertrekt.',
                                         owner=self)

        self._doelAssetId = OTLAttribuut(field=DtcIdentificator,
                                         naam='doelAssetId',
                                         label='asset-id doel-asset',
                                         objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#RelatieObject.doelAssetId',
                                         definition='De identificator van het object waarin de relatie toekomt.',
                                         owner=self)

    @property
    def assetId(self) -> DtcIdentificatorWaarden:
        """Unieke identificatie van de asset zoals toegekend door de assetbeheerder of n.a.v. eerste aanlevering door de leverancier."""
        return self._assetId.get_waarde()

    @assetId.setter
    def assetId(self, value):
        self._assetId.set_waarde(value, owner=self)

    @property
    def bronAssetId(self) -> DtcIdentificatorWaarden:
        """De identificator van het object waaruit de relatie vertrekt."""
        return self._bronAssetId.get_waarde()

    @bronAssetId.setter
    def bronAssetId(self, value):
        self._bronAssetId.set_waarde(value, owner=self)

    @property
    def doelAssetId(self) -> DtcIdentificatorWaarden:
        """De identificator van het object waarin de relatie toekomt."""
        return self._doelAssetId.get_waarde()

    @doelAssetId.setter
    def doelAssetId(self, value):
        self._doelAssetId.set_waarde(value, owner=self)
