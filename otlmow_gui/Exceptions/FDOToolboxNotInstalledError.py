from otlmow_gui.Domain import global_vars


class FDOToolboxNotInstalledError(Exception):
    def __init__(self, language):
        self._ = language

        super().__init__()

    def __str__(self):
        # "FDO toolbox executable could not be found. Most likely because it is not installed (correctly), "
        # "You can rerun the OTL wizard installer with admin privileges to fix this error."
        # "Make sure it is installed in the correct directory so that the following path exists: \n{0}"
        translation = self._("FDOToolbox_not_installed_error_message")
        return translation.format(global_vars.FDO_toolbox_path_str, global_vars.FDO_toolbox_installer_path_str)