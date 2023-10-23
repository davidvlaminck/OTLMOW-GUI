import gettext


class LanguageSettings:

    def __init__(self):
        self.language = 'en'

    # Switchen kan door in language en of nl_BE in te geven
    def return_language(self):
        print("This function returns " + self.language)
        translator = gettext.translation('messages', localedir='../locale/', languages=[self.language])
        translator.install()
        return translator.gettext

    def setLanguage(self, language):
        print("Changing language to: " + language)
        self.language = language
        print("Language now saved as " + self.language)
