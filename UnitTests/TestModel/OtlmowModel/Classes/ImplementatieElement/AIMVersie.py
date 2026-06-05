# coding=utf-8
from ...BaseClasses.OTLObject import OTLAttribuut
from abc import abstractmethod, ABC
from ...Datatypes.DtcAssetVersie import DtcAssetVersie, DtcAssetVersieWaarden


# Generated with OTLClassCreator. To modify: extend, do not edit
class AIMVersie(ABC):
    """Abstracte klasse met de eigenschappen om de versionering van een asset te beheren."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMVersie'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    @abstractmethod
    def __init__(self):
        super().__init__()

        self._assetVersie = OTLAttribuut(field=DtcAssetVersie,
                                         naam='assetVersie',
                                         label='asset-versie',
                                         objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMVersie.assetVersie',
                                         definition='De versie van de asset in de database.',
                                         owner=self)

    @property
    def assetVersie(self) -> DtcAssetVersieWaarden:
        """De versie van de asset in de database."""
        return self._assetVersie.get_waarde()

    @assetVersie.setter
    def assetVersie(self, value):
        self._assetVersie.set_waarde(value, owner=self)
