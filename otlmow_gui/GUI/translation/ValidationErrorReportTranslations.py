from otlmow_converter.Exceptions.FailedToImportFileError import FailedToImportFileError
from otlmow_converter.Exceptions.InvalidColumnNamesInExcelTabError import \
    InvalidColumnNamesInExcelTabError
from otlmow_converter.Exceptions.NoTypeUriInTableError import NoTypeUriInTableError
from otlmow_converter.Exceptions.TypeUriNotInFirstRowError import TypeUriNotInFirstRowError

from otlmow_gui.Exceptions.NoIdentificatorError import NoIdentificatorError
from otlmow_gui.Exceptions.RelationHasInvalidTypeUriForSourceAndTarget import \
    RelationHasInvalidTypeUriForSourceAndTarget
from otlmow_gui.Exceptions.RelationHasNonExistingTypeUriForSourceOrTarget import \
    RelationHasNonExistingTypeUriForSourceOrTarget
from otlmow_gui.GUI.translation.GlobalTranslate import GlobalTranslate


class ValidationErrorReportTranslations:



    @classmethod
    def translate_exception(cls, doc_name, exception):
        if str(exception) == "argument of type 'NoneType' is not iterable":
            error_text = GlobalTranslate._(
                "{doc_name}: Data nodig in een datasheet om objecten in te laden.\n").format(
                doc_name=doc_name)
        elif issubclass(type(exception), NoTypeUriInTableError):
            error_text = GlobalTranslate._(
                "{doc_name}: No type uri in {tab}\n").format(
                doc_name=doc_name, tab=str(exception.tab))
        elif issubclass(type(exception), InvalidColumnNamesInExcelTabError):
            error_text = GlobalTranslate._(
                "{doc_name}: invalid columns in {tab}, bad columns are {bad_columns} \n").format(
                doc_name=doc_name, tab=exception.tab, bad_columns=str(exception.bad_columns))
        elif issubclass(type(exception), TypeUriNotInFirstRowError):
            error_text = GlobalTranslate._(
                "{doc_name}: type uri not in first row of {tab}\n").format(
                doc_name=doc_name, tab=str(exception.tab))
        elif issubclass(type(exception),
                        FailedToImportFileError):  # as of otlmow_converter==1.4 never instantiated
            error_text = GlobalTranslate._(f'{doc_name}: {exception} \n')
        elif issubclass(type(exception), NoIdentificatorError):
            error_text = GlobalTranslate._(
                "{doc_name}: There are assets without an assetId.identificator in "
                "worksheet {tab}\n").format(doc_name=doc_name, tab=str(exception.tab))
        elif issubclass(type(exception), RelationHasInvalidTypeUriForSourceAndTarget):
            error_text = GlobalTranslate._(
                "{doc_name}:\n" +
                "Relation of type: \"{type_uri}\"\n" +
                "with assetId.identificator: \"{identificator}\"\n" +
                "This relation cannot be made between the typeURI's.\n" +
                "{wrong_field}= \"{wrong_value}\"\n" +
                "{wrong_field2}= \"{wrong_value2}\"\nin tab {tab}\n").format(
                doc_name=doc_name,
                type_uri=exception.relation_type_uri,
                identificator=exception.relation_identificator,
                wrong_field=exception.wrong_field,
                wrong_value=exception.wrong_value,
                wrong_field2=exception.wrong_field2,
                wrong_value2=exception.wrong_value2,
                tab=exception.tab)
        elif issubclass(type(exception), RelationHasNonExistingTypeUriForSourceOrTarget):
            error_text = GlobalTranslate._(
                "{doc_name}:\n"
                "Relation of type: \"{type_uri}\"\n"
                "with assetId.identificator: \"{identificator}\",\n"
                "has the non-existing TypeURI value: \"{wrong_value}\"\n"
                "for field \"{wrong_field}\".\nin tab {tab}\n").format(
                doc_name=doc_name,
                type_uri=exception.relation_type_uri,
                identificator=exception.relation_identificator,
                wrong_field=exception.wrong_field,
                wrong_value=exception.wrong_value,
                tab=exception.tab)

        else:
            error_text = GlobalTranslate._(f'{doc_name}: {exception}\n')
        return error_text