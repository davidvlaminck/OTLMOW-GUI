from collections import defaultdict
from pathlib import Path

from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_converter.Exceptions.CannotCombineAssetsError import CannotCombineAssetsError
from otlmow_converter.Exceptions.CannotCombineDifferentAssetsError import \
    CannotCombineAssetsWithDifferentIdError, CannotCombineAssetsWithDifferentTypeError
from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
from otlmow_converter.Exceptions.NoIdentificatorError import NoIdentificatorError
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject

from otlmow_gui.GUI.translation.GlobalTranslate import GlobalTranslate


class CombineAssetHelper:
    @classmethod
    def combine_assets(cls,asset_list: list[OTLObject], model_directory: Path = None) -> list[
        OTLObject]:
        assets = defaultdict(list)
        for asset in asset_list:
            if asset.typeURI == 'http://purl.org/dc/terms/Agent':
                assets[asset.agentId.identificator].append(asset)
            else:
                assets[asset.assetId.identificator].append(asset)
        combined_assets = []

        list_of_errors = []
        for asset_list in assets.values():

            try:
                if len(asset_list) == 1:
                    combined_assets.append(asset_list[0])
                else:
                    combined_asset = cls.combine_two_asset_instances(asset_list[0], asset_list[1],
                                                                 model_directory)
                    for asset in asset_list[2:]:
                        combined_asset = cls.combine_two_asset_instances(combined_asset, asset,
                                                                     model_directory)
                    combined_assets.append(combined_asset)

            except CannotCombineAssetsWithDifferentTypeError as ex:
                object_id = ex.object_id
                short_uri = ""
                short_uri_2 = ""
                if ex.attribute_errors and ex.attribute_errors[0][0] == 'typeURI':
                    short_uri = ex.attribute_errors[0][1][0].split('/')[-1]
                    short_uri_2 = ex.attribute_errors[0][1][1].split('/')[-1]

                ex.message = (GlobalTranslate._('Cannot combine the assets with id: "{object_id}"\n'
                              'due to conflicting types: {short_uri} != {short_uri_2}').format(object_id=object_id,short_uri=short_uri,short_uri_2=short_uri_2))

                ex.args = ex.message,
                list_of_errors.append(ex)
            except CannotCombineAssetsError as ex:
                object_id = ex.object_id
                short_uri = ex.type_uri.split('/')[-1]
                error_str = '\n'.join(
                    [f'{t[0]}: {t[1][0]} != {t[1][1]}' for t in ex.attribute_errors])

                ex.message = (
                        GlobalTranslate._('Cannot combine the assets with id: "{object_id}" with type "{short_uri}"\n'
                        'due to conflicting values in attribute(s):\n').format(object_id=object_id,short_uri=short_uri) + error_str)

                ex.args = ex.message,

                list_of_errors.append(ex)
        if list_of_errors:
            raise ExceptionsGroup(
                message= GlobalTranslate._('There were errors while combining the assets'),
                exceptions=list_of_errors
            )

        return combined_assets

    @classmethod
    def combine_two_asset_instances(cls,asset1: OTLObject, asset2: OTLObject,
                                    model_directory: Path = None) -> OTLObject:
        if asset1 is None or asset2 is None:
            raise ValueError('One of the assets is None')

        id1 = asset1.assetId.identificator if asset1.typeURI != 'http://purl.org/dc/terms/Agent' \
            else asset1.agentId.identificator
        id2 = asset2.assetId.identificator if asset2.typeURI != 'http://purl.org/dc/terms/Agent' \
            else asset2.agentId.identificator

        if id1 is None or id2 is None:
            raise NoIdentificatorError('One of the assets has no assetId.identificator')

        if id1 != id2:
            ex = CannotCombineAssetsWithDifferentIdError(
                'The assets have different identificator values')
            ex.attribute_errors = [('identificator', (id1, id2))]
            ex.type_uri = asset1.typeURI
            raise ex

        if asset1.typeURI != asset2.typeURI:
            ex = CannotCombineAssetsWithDifferentTypeError('The assets have different types')
            ex.attribute_errors = [('typeURI', (asset1.typeURI, asset2.typeURI))]
            ex.object_id = id1
            raise ex

        ddict1 = DotnotationDictConverter.to_dict(asset1)
        ddict2 = DotnotationDictConverter.to_dict(asset2)
        if asset2.typeURI == 'http://purl.org/dc/terms/Agent':
            ddict2.pop('agentId.identificator')
        else:
            ddict2.pop('assetId.identificator')

        attribute_errors = []
        for key, value in ddict2.items():
            if value is None:
                continue
            if key == 'typeURI':
                continue

            if key in ddict1 and ddict1[key] is not None and ddict1[key] != value:
                attribute_errors.append((key, ddict1[key], value))
            else:
                ddict1[key] = value

        if attribute_errors:
            error_str = '\n'.join(
                [f'{key}: {ddict1[key]}, {value}' for key, _, value in sorted(attribute_errors)])
            ex = CannotCombineAssetsError(
                message=f'Cannot combine the assets with id {id1} because some attributes '
                        'have conflicting values:\n'
                        f'{error_str}')
            ex.object_id = id1
            ex.type_uri = asset1.typeURI
            ex.attribute_errors = [(key, (ddict1[key], value)) for key, _, value in
                                   attribute_errors]
            raise ex

        return DotnotationDictConverter.from_dict(ddict1, model_directory=model_directory)