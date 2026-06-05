# coding=utf-8
from ..BaseClasses.OTLObject import OTLAttribuut
from ..Datatypes.KwantWrdTest import KwantWrdTest, KwantWrdTestWaarden
from ..BaseClasses.StringField import StringField
from ..BaseClasses.UnionTypeField import UnionTypeField
from ..BaseClasses.UnionWaarden import UnionWaarden


# Generated with OTLUnionDatatypeCreator. To modify: extend, do not edit
class DtuTestUnionTypeWaarden(UnionWaarden):
    def __init__(self):
        UnionWaarden.__init__(self)
        self._unionKwantWrd = OTLAttribuut(field=KwantWrdTest,
                                           naam='unionKwantWrd',
                                           label='Union kwantitatieve waarde',
                                           objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtuTestUnionType.unionKwantWrd',
                                           kardinaliteit_min='0',
                                           definition='Kwantitatieve waarde van het test Union datatype',
                                           owner=self)

        self._unionString = OTLAttribuut(field=StringField,
                                         naam='unionString',
                                         label='Union tekstveld',
                                         objectUri='https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtuTestUnionType.unionString',
                                         kardinaliteit_min='0',
                                         definition='Vrij tekstveld van het test Union datatype',
                                         owner=self)

    @property
    def unionKwantWrd(self) -> KwantWrdTestWaarden:
        """Kwantitatieve waarde van het test Union datatype"""
        return self._unionKwantWrd.get_waarde()

    @unionKwantWrd.setter
    def unionKwantWrd(self, value):
        self._unionKwantWrd.set_waarde(value, owner=self._parent)
        if value is not None:
            self.clear_other_props('_unionKwantWrd')

    @property
    def unionString(self) -> str:
        """Vrij tekstveld van het test Union datatype"""
        return self._unionString.get_waarde()

    @unionString.setter
    def unionString(self, value):
        self._unionString.set_waarde(value, owner=self._parent)
        if value is not None:
            self.clear_other_props('_unionString')


# Generated with OTLUnionDatatypeCreator. To modify: extend, do not edit
class DtuTestUnionType(UnionTypeField):
    """Union datatype voor test doeleinden."""
    naam = 'DtuTestUnionType'
    label = 'Test UnionType'
    objectUri = 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#DtuTestUnionType'
    definition = 'Union datatype voor test doeleinden.'
    waardeObject = DtuTestUnionTypeWaarden

    def __str__(self):
        return UnionTypeField.__str__(self)

