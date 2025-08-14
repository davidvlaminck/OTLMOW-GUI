from otlmow_converter.Exceptions.UnknownExcelError import UnknownExcelError


class RelationHasNonExistingTypeUriForSourceOrTarget(UnknownExcelError):
    """
    The bronAssetID.typeURI or doelAssetID.typeURI do NOT EXIST as real TypeUri's
    This precludes the fact that these typeURI's are invalid for the current relationTypeURI
    """
    def __init__(self,relation_type_uri,relation_identificator,wrong_field,wrong_value,tab=None,*args):
        super().__init__(Exception(),*args)
        self.relation_type_uri = relation_type_uri
        self.relation_identificator = relation_identificator
        self.wrong_field = wrong_field
        self.wrong_value = wrong_value
        self.tab = tab