from otlmow_model.OtlmowModel.BaseClasses.OTLObject import create_dict_from_asset
from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import compare_two_lists_of_objects_attribute_level

from Domain.enums import ReportAction
from Domain.report_item import ReportItem


class AssetChangeDomain:

    @classmethod
    def generate_diff_report(cls, original_data, new_data, model_directory):
        report = []
        diff_1 = compare_two_lists_of_objects_attribute_level(first_list=original_data, second_list=new_data,
                                                              model_directory=model_directory)
        diff_2 = compare_two_lists_of_objects_attribute_level(first_list=original_data, second_list=diff_1, )
        for item in diff_2:
            old_item = next((x for x in original_data if x.assetId.identificator == item.assetId.identificator), None)
            if old_item is None:
                rep_item = ReportItem(
                    id=item.assetId.identificator,
                    actie=ReportAction.ASS,
                    attribute="",
                    original_value="",
                    new_value=""
                )
                report.append(rep_item)
            else:
                item_dict = create_dict_from_asset(item)
                old_item_dict = create_dict_from_asset(old_item)
                item_id = item_dict.get('assetId').get('identificator')
                for key, value in item_dict.items():
                    if key == 'assetId' or key == 'typeURI':
                        continue
                    else:
                        if isinstance(value, dict):
                            for k, v in value.items():
                                rep_item = ReportItem(
                                    id=item_id,
                                    actie=ReportAction.ATC,
                                    attribute=str(key),
                                    original_value=str(k) + ": " + str(old_item_dict.get(key).get(k)),
                                    new_value=str(k) + ": " + str(v)
                                )
                                report.append(rep_item)
                        else:
                            rep_item = ReportItem(
                                id=item_id,
                                actie=ReportAction.ATC,
                                attribute=str(key),
                                original_value=str(old_item_dict.get(key)),
                                new_value=str(value)
                            )
                            report.append(rep_item)
        return report