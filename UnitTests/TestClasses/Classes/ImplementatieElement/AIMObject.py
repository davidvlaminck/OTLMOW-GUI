# coding=utf-8
from datetime import date
from typing import List
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLAttribuut
from abc import abstractmethod
from ...Classes.ImplementatieElement.AIMDBStatus import AIMDBStatus
from ...Classes.ImplementatieElement.AIMToestand import AIMToestand
from otlmow_model.OtlmowModel.BaseClasses.OTLAsset import OTLAsset
from otlmow_model.OtlmowModel.BaseClasses.RelationInteractor import RelationInteractor
from otlmow_model.OtlmowModel.BaseClasses.DateField import DateField
from ...Datatypes.DtcIdentificator import DtcIdentificator, DtcIdentificatorWaarden
from ...Datatypes.KwantWrdInMaand import KwantWrdInMaand, KwantWrdInMaandWaarden
from otlmow_model.OtlmowModel.BaseClasses.StringField import StringField


# Generated with OTLClassCreator. To modify: extend, do not edit
class AIMObject(AIMDBStatus, AIMToestand, OTLAsset, RelationInteractor):
    """Abstracte als de basisklasse voor alle uniek geïdentificeerde OTL objecten met de basiseigenschappen die elk OTL object minstens heeft."""

    typeURI = 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject'
    """De URI van het object volgens https://www.w3.org/2001/XMLSchema#anyURI."""

    @abstractmethod
    def __init__(self):
        super().__init__()

        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Bevestiging', target='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#Derdenobject')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HeeftAanvullendeGeometrie', target='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#AanvullendeGeometrie')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HeeftBetrokkene', target='http://purl.org/dc/terms/Agent')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HeeftBijlage', target='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#Bijlage')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HeeftToegangsprocedure', target='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#Toegangsprocedure')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#LigtOp', target='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#Derdenobject')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#SluitAanOp', target='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#Derdenobject')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Sturing', target='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#Derdenobject')
        self.add_valid_relation(relation='https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Voedt', target='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#Derdenobject')

        self._assetId = OTLAttribuut(field=DtcIdentificator,
                                     naam='assetId',
                                     label='asset-id',
                                     objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.assetId',
                                     definition='Unieke identificatie van de asset zoals toegekend door de assetbeheerder of n.a.v. eerste aanlevering door de leverancier.',
                                     owner=self)

        self._bestekPostNummer = OTLAttribuut(field=StringField,
                                              naam='bestekPostNummer',
                                              label='bestekpostnummer',
                                              objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.bestekPostNummer',
                                              usagenote='Bevat de specifieke identificatie binnen een bestek van een post in de meetstaat. De notatie kan eender welke codering aannemen, bv. in de vorm van een nummer, id of tekst naargelang de notatie in het specifieke bestek.',
                                              kardinaliteit_max='*',
                                              definition='Een verwijzing naar een postnummer uit het specifieke bestek waar het object mee verband houdt.',
                                              owner=self)

        self._datumOprichtingObject = OTLAttribuut(field=DateField,
                                                   naam='datumOprichtingObject',
                                                   label='datum oprichting object',
                                                   objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.datumOprichtingObject',
                                                   definition='De datum waarop het object op het terrein is beginnen bestaan, bv. de datum van aanleg.',
                                                   owner=self)

        self._notitie = OTLAttribuut(field=StringField,
                                     naam='notitie',
                                     label='notitie',
                                     objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.notitie',
                                     definition='Extra notitie voor het object.',
                                     owner=self)

        self._standaardBestekPostNummer = OTLAttribuut(field=StringField,
                                                       naam='standaardBestekPostNummer',
                                                       label='standaardbestekpostnummer',
                                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.standaardBestekPostNummer',
                                                       kardinaliteit_max='*',
                                                       definition='Een verwijzing naar een postnummer uit het standaardbestek waar het object mee verband houdt. De notatie van het postnummer moet overeenkomen met de notatie die gebruikt is in de catalogi van standaardbestekken, bijvoorbeeld postnummer 0701.20404G.',
                                                       owner=self)

        self._theoretischeLevensduur = OTLAttribuut(field=KwantWrdInMaand,
                                                    naam='theoretischeLevensduur',
                                                    label='theoretische levensduur',
                                                    objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#AIMObject.theoretischeLevensduur',
                                                    definition='De levensduur in aantal maanden die theoretisch mag verwacht worden voor een object.',
                                                    owner=self)

    @property
    def assetId(self) -> DtcIdentificatorWaarden:
        """Unieke identificatie van de asset zoals toegekend door de assetbeheerder of n.a.v. eerste aanlevering door de leverancier."""
        return self._assetId.get_waarde()

    @assetId.setter
    def assetId(self, value):
        self._assetId.set_waarde(value, owner=self)

    @property
    def bestekPostNummer(self) -> List[str]:
        """Een verwijzing naar een postnummer uit het specifieke bestek waar het object mee verband houdt."""
        return self._bestekPostNummer.get_waarde()

    @bestekPostNummer.setter
    def bestekPostNummer(self, value):
        self._bestekPostNummer.set_waarde(value, owner=self)

    @property
    def datumOprichtingObject(self) -> date:
        """De datum waarop het object op het terrein is beginnen bestaan, bv. de datum van aanleg."""
        return self._datumOprichtingObject.get_waarde()

    @datumOprichtingObject.setter
    def datumOprichtingObject(self, value):
        self._datumOprichtingObject.set_waarde(value, owner=self)

    @property
    def notitie(self) -> str:
        """Extra notitie voor het object."""
        return self._notitie.get_waarde()

    @notitie.setter
    def notitie(self, value):
        self._notitie.set_waarde(value, owner=self)

    @property
    def standaardBestekPostNummer(self) -> List[str]:
        """Een verwijzing naar een postnummer uit het standaardbestek waar het object mee verband houdt. De notatie van het postnummer moet overeenkomen met de notatie die gebruikt is in de catalogi van standaardbestekken, bijvoorbeeld postnummer 0701.20404G."""
        return self._standaardBestekPostNummer.get_waarde()

    @standaardBestekPostNummer.setter
    def standaardBestekPostNummer(self, value):
        self._standaardBestekPostNummer.set_waarde(value, owner=self)

    @property
    def theoretischeLevensduur(self) -> KwantWrdInMaandWaarden:
        """De levensduur in aantal maanden die theoretisch mag verwacht worden voor een object."""
        return self._theoretischeLevensduur.get_waarde()

    @theoretischeLevensduur.setter
    def theoretischeLevensduur(self, value):
        self._theoretischeLevensduur.set_waarde(value, owner=self)
