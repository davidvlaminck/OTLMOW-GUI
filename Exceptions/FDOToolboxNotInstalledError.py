from Domain import global_vars


class FDOToolboxNotInstalledError(Exception):
    def __init__(self, language):
        self._ = language

        super().__init__()

    def __str__(self):
        translation = self._(
            "FDO toolbox executable could not be found. Most likely because it is not installed. Make sure it is installed in the correct directory so that the following path exists: \n{0}")
        return translation.format(global_vars.FDO_toolbox_path_str)