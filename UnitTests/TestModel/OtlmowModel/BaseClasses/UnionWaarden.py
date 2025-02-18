from otlmow_model.OtlmowModel.BaseClasses.WaardenObject import WaardenObject


class UnionWaarden(WaardenObject):
    def __init__(self):
        super().__init__()

    def clear_other_props(self, prop_name: str):
        prop_name = prop_name[1:]
        for attribute in self:
            if attribute.naam == prop_name:
                continue
            if attribute.field.waardeObject is not None and not attribute.field.waarde_shortcut_applicable:
                setattr(attribute.waarde, 'waarde', None)
            else:
                setattr(attribute, 'waarde', None)
