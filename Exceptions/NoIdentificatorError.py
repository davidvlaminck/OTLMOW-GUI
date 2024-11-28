from otlmow_converter.Exceptions.UnknownExcelError import UnknownExcelError


class NoIdentificatorError(UnknownExcelError):


    def __str__(self):
        if self.tab:
            return f"There are assets without an assetId.identificator in worksheet {self.tab}"
        else:
            return super().__str__()