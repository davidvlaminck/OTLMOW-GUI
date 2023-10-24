import gettext
import logging
import warnings


class LanguageSettings:

    def __init__(self):
        self.language = 'en'

    # Switchen kan door in language en of nl_BE in te geven
    def return_language(self):
        logging.info("This function returns " + self.language)
        translator = gettext.translation('messages', localedir='../locale/', languages=[self.language])
        translator.install()
        return translator.gettext

    def set_language(self, language : str):
        if language == 'nl_BE' or language == 'en':
            self.language = language
        else:
            warnings.warn("Language not supported, switching to default language: en")
            self.language = 'en'
