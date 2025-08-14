from otlmow_converter.Exceptions.UnknownExcelError import UnknownExcelError


class NoIdentificatorError(UnknownExcelError):


    def __init__(self,language, original_exception, tab: str = None):
        self._ = language
        super().__init__(original_exception, tab)

    def __str__(self):
        if self.tab:
            translation = self._("There are assets without an assetId.identificator in worksheet {0}")
            return translation.format(self.tab)
        else:
            return super().__str__()