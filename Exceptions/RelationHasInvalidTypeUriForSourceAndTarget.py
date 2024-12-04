from otlmow_converter.Exceptions.UnknownExcelError import UnknownExcelError


class RelationHasInvalidTypeUriForSourceAndTarget(UnknownExcelError):
    """
    The bronAssetID.typeURI and doelAssetID.typeURI are INVALID for the current relationTypeURI
    For this error to occur the bronAssetID.typeURI or doelAssetID.typeURI need to exist first otherwise
    Error RelationHasNonExistingTypeUriForSourceOrTarget is thrown
    """
    def __init__(self,relation_type_uri,relation_identificator,wrong_field,wrong_value,wrong_field2= None,wrong_value2 = None,tab=None,*args):
        super().__init__(Exception(),*args)
        self.relation_type_uri = relation_type_uri
        self.relation_identificator = relation_identificator
        self.wrong_field = wrong_field
        self.wrong_value = wrong_value
        self.wrong_field2 = wrong_field2
        self.wrong_value2 = wrong_value2
        self.tab = tab

