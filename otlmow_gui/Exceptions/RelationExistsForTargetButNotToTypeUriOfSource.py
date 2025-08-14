
class RelationExistsForTargetButNotToTypeUriOfSource(Exception):
    """
    The bronAssetID.typeURI is INVALID for the current relationTypeURI and doelAssetID.typeURI
    For this error to occur the bronAssetID.typeURI or doelAssetID.typeURI need to exist first otherwise
    Error RelationHasNonExistingTypeUriForSourceOrTarget is thrown
    """
    def __init__(self,relation_type_uri,relation_identificator,wrong_field,wrong_value,*args):
        super().__init__(Exception(),*args)
        self.relation_type_uri = relation_type_uri
        self.relation_identificator = relation_identificator
        self.wrong_field = wrong_field
        self.wrong_value = wrong_value

