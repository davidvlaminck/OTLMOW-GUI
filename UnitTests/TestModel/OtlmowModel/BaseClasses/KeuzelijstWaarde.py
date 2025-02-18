class KeuzelijstWaarde:
    def __init__(self, invulwaarde: str = '', label: str = '', definitie: str = '', objectUri: str = '',
                 status: str = ''):
        self.invulwaarde: str = invulwaarde
        self.label: str = label
        self.definitie: str = definitie
        self.objectUri: str = objectUri
        self.status: str = status

    def __str__(self) -> str:
        if self.status in {'', 'ingebruik'}:
            return self.invulwaarde

        return f'{self.invulwaarde} ({self.status})'
