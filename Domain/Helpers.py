from otlmow_model.OtlmowModel.Helpers.generated_lists import get_hardcoded_class_dict

from GUI.screens.RelationChange_elements.RelationChangeHelpers import RelationChangeHelpers


class Helpers:
    all_OTL_asset_types_dict = {}

    @classmethod
    def create_external_typeURI_options(cls):
        all_type_uris = get_hardcoded_class_dict()
        for uri, info in all_type_uris.items():
            abbr_type_uri = RelationChangeHelpers.get_abbreviated_typeURI(uri, add_namespace=True)
            screen_name = info['label']
            if "#" in abbr_type_uri:
                abbr_type_uri_split = abbr_type_uri.split("#")
                screen_name = "#".join([screen_name, abbr_type_uri_split[0]])

            cls.all_OTL_asset_types_dict[screen_name] = uri
        cls.all_OTL_asset_types_dict = Helpers.sort_nested_dict(cls.all_OTL_asset_types_dict)

    @classmethod
    def sort_nested_dict(cls, d, by='keys'):
        """Recursively sorts a dictionary by keys or values."""
        if not isinstance(d, dict):
            if isinstance(d, list):
                return sorted(d, key=lambda relation_object: relation_object.typeURI)
            return d

        # Sort the current dictionary
        if by == 'keys':
            sorted_dict = dict(
                (k, cls.sort_nested_dict(v, by=by)) for k, v in sorted(d.items())
            )
        elif by == 'values':
            sorted_dict = dict(
                (k, cls.sort_nested_dict(v, by=by)) for k, v in
                sorted(d.items(), key=lambda item: item[1])
            )
        else:
            raise ValueError("Invalid sort parameter. Use 'keys' or 'values'.")

        return sorted_dict