from abc import abstractmethod

from otlmow_model.OtlmowModel.GeometrieTypes.AbstracteGeometrie import AbstracteGeometrie


class PuntGeometrie(AbstracteGeometrie):
    @abstractmethod
    def __init__(self):
        super().__init__()
        self._geometry_types.append('POINT Z')
