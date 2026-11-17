from otlmow_gui.GUI.screens.Screen import Screen


class InfoTemplateScreen(Screen):
    """Placeholder screen for the info template tab.

    This tab is intentionally left empty for now.
    """

    def __init__(self, language_settings=None):
        super().__init__()
        self._ = language_settings

    def reset_ui(self, _):
        pass
