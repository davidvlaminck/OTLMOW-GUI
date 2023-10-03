# coding=utf-8
import random
from otlmow_model.BaseClasses.KeuzelijstField import KeuzelijstField
from otlmow_model.BaseClasses.KeuzelijstWaarde import KeuzelijstWaarde


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
                                        definitie='geannuleerd',
                                        objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAIMToestand/geannuleerd'),
        'gepland': KeuzelijstWaarde(invulwaarde='gepland',
                                    label='gepland',
                                    status='ingebruik',
                                    definitie='gepland',
                                    objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAIMToestand/gepland'),
        'in-gebruik': KeuzelijstWaarde(invulwaarde='in-gebruik',
                                       label='in-gebruik',
                                       status='ingebruik',
                                       definitie='in-gebruik',
                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAIMToestand/in-gebruik'),
        'in-ontwerp': KeuzelijstWaarde(invulwaarde='in-ontwerp',
                                       label='in-ontwerp',
                                       status='ingebruik',
                                       definitie='in-ontwerp',
                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAIMToestand/in-ontwerp'),
        'in-opbouw': KeuzelijstWaarde(invulwaarde='in-opbouw',
                                      label='in-opbouw',
                                      status='ingebruik',
                                      definitie='in-opbouw',
                                      objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAIMToestand/in-opbouw'),
        'overgedragen': KeuzelijstWaarde(invulwaarde='overgedragen',
                                         label='overgedragen',
                                         status='ingebruik',
                                         definitie='overgedragen',
                                         objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAIMToestand/overgedragen'),
        'uit-gebruik': KeuzelijstWaarde(invulwaarde='uit-gebruik',
                                        label='uit-gebruik',
                                        status='ingebruik',
                                        definitie='uit-gebruik',
                                        objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAIMToestand/uit-gebruik'),
        'verwijderd': KeuzelijstWaarde(invulwaarde='verwijderd',
                                       label='verwijderd',
                                       status='ingebruik',
                                       definitie='verwijderd',
                                       objectUri='https://wegenenverkeer.data.vlaanderen.be/id/concept/KlAIMToestand/verwijderd')
    }

    @classmethod
    def create_dummy_data(cls):
        return cls.create_dummy_data_keuzelijst(cls.options)

