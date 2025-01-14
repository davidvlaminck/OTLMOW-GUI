
class FDOToolboxProcessError(Exception):
    def __init__(self, language, command: str, fdo_toolbox_error:str):
        self._ = language
        self.command = command
        self.fdo_toolbox_error = fdo_toolbox_error

        super().__init__()

    def __str__(self):
        translation = self._(
            "An error occured during FDO toolbox call:  \nCall: {0} \nError:\n{1}")
        return translation.format(self.command, self.fdo_toolbox_error)