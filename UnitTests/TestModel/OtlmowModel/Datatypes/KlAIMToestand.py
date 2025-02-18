# coding=utf-8
from otlmow_model.OtlmowModel.BaseClasses.KeuzelijstField import KeuzelijstField
from otlmow_model.OtlmowModel.BaseClasses.KeuzelijstWaarde import KeuzelijstWaarde


# Generated with OTLEnumerationCreator. To modify: extend, do not edit
class KlAIMToestand(KeuzelijstField):
    """Keuzelijst met fasen uit de levenscyclus van een object om de toestand op een moment mee vast te leggen."""
    naam = 'KlAIMToestand'
    label = 'AIM toestand'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#KlAIMToestand'
    definition = 'Keuzelijst met fasen uit de levenscyclus van een object om de toestand op een moment mee vast te leggen.'
    status = 'ingebruik'
    codelist = 'https://wegenenverkeer.data.vlaanderen.be/id/conceptscheme/KlAIMToestand'
    options = {
        'geannuleerd': KeuzelijstWaarde(invulwaarde='geannuleerd',
                                        label='geannuleerd',
                                        status='ingebruik',
                                        definitie='Het object werd ontworpen maar het ontwerpproces is stopgezet.',
                                        objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAIMToestand/geannuleerd'),
        'gepland': KeuzelijstWaarde(invulwaarde='gepland',
                                    label='gepland',
                                    status='ingebruik',
                                    definitie='  AIM toestand na ontwerp en voor start opbouw of installatie. Start na het uitsturen van het dienstbevel voor aanvang werken.',
                                    objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAIMToestand/gepland'),
        'in-gebruik': KeuzelijstWaarde(invulwaarde='in-gebruik',
                                       label='in gebruik',
                                       status='ingebruik',
                                       definitie='Het object vervult zijn functie.',
                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAIMToestand/in-gebruik'),
        'in-ontwerp': KeuzelijstWaarde(invulwaarde='in-ontwerp',
                                       label='in ontwerp',
                                       status='ingebruik',
                                       definitie='Het (virtueel) object wordt geselecteerd, geconfigureerd en beschreven. Zowel van toepassing op een voorontwerp als definitief ontwerp.',
                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAIMToestand/in-ontwerp'),
        'in-opbouw': KeuzelijstWaarde(invulwaarde='in-opbouw',
                                      label='in opbouw',
                                      status='ingebruik',
                                      definitie='  Het object wordt geïmplementeerd of opgebouwd op het terrein en geïnventariseerd.',
                                      objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAIMToestand/in-opbouw'),
        'overgedragen': KeuzelijstWaarde(invulwaarde='overgedragen',
                                         label='overgedragen',
                                         status='ingebruik',
                                         definitie='Het object was in het beheer van AWV en werd overgedragen aan een andere organisatie of onderneming.',
                                         objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAIMToestand/overgedragen'),
        'uit-gebruik': KeuzelijstWaarde(invulwaarde='uit-gebruik',
                                        label='uit gebruik',
                                        status='ingebruik',
                                        definitie='Het object vervult geen functie (meer) en is fysiek (deels) nog/al aanwezig op het terrein.',
                                        objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAIMToestand/uit-gebruik'),
        'verwijderd': KeuzelijstWaarde(invulwaarde='verwijderd',
                                       label='verwijderd',
                                       status='ingebruik',
                                       definitie='  Het object vervult geen functie meer en is fysiek niet meer aanwezig op het terrein.',
                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAIMToestand/verwijderd')
    }

    @classmethod
    def create_dummy_data(cls):
        return cls.create_dummy_data_keuzelijst(cls.options)

