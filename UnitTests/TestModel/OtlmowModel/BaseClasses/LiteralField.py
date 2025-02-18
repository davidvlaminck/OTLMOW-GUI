from otlmow_model.OtlmowModel.BaseClasses.StringField import StringField


class LiteralField(StringField):
    def __init__(self):
        StringField.__init__(self)

    def __str__(self) -> str:
        return StringField.__str__(self)
