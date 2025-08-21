import datetime
import gettext
import json
import logging
import platform
from pathlib import Path

from otlmow_gui.Domain.enums import Language
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.ProgramFileStructure import ProgramFileStructure


class Settings:
    settings_filename = 'settings.json'

    @classmethod
    def return_language(cls, locale_dir: Path, language: Language = Language.DUTCH):
        """
        Sets the application's language by loading the appropriate translation files.

        This class method retrieves the translation for the specified language from the given
        locale directory, defaulting to Dutch if no language is provided.

        :param locale_dir: The directory where the translation files are located.
        :type locale_dir: Path
        :param language: The language to be set for translations. If not provided, defaults to
        Language.DUTCH.
        :type language: Language, optional

        :return: A gettext function that can be used to translate messages.
        :rtype: function

        :raises Exception: If there is an error loading the translation files.

        :example:
            translator = Settings.return_language(Path('/path/to/locales'), Language.ENGLISH)

        Falls back to returning the original string if no translation is found.
        """
        language_str = str(language)
        logging.debug(f"Changing language to: {language_str}")

        try:
            translator = gettext.translation(
                'messages',
                localedir=locale_dir,
                languages=[language.value]
            )
            translator.install()
            return translator.gettext
        except FileNotFoundError:
            OTLLogger.logger.warning(
                f"Translation file for '{language.value}' not found in {locale_dir}. "
                "Falling back to identity translation."
            )
            return lambda x: x
        except Exception as e:
            OTLLogger.logger.error(f"Error loading translations for {language.value}: {e}")
            return lambda x: x

    @classmethod
    def get_or_create_settings_file(cls) -> dict:
        """
        Retrieves or creates a settings file for the application.

        This class method checks for the existence of a settings file and initializes it with
        default values if it does not exist, including the operating system, language, and run
        timestamps.

        :return: A dictionary containing the settings details, including language, operating system, first run status, and last run timestamp.
        :rtype: dict

        :raises IOError: If there is an error reading or writing the settings file.

        :example:
            settings = Settings.get_or_create_settings_file()
        """


        work_dir_path = ProgramFileStructure.get_otl_wizard_work_dir()
        settings_filepath = work_dir_path / 'settings.json'
        first_run = not settings_filepath.exists()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        operating_sys = platform.system()
        language = Language.DUTCH


        settings_details = cls.load_settings(settings_filepath)

        if not settings_details.__contains__('language'):
            settings_details['language'] = str(language.name)

        settings_details['OS'] = str(operating_sys)
        settings_details['first_run'] = first_run
        settings_details['last_run'] = timestamp

        cls.save_settings(settings_details, settings_filepath)

        return settings_details

    @classmethod
    def save_settings(cls, settings_details, settings_filepath):
        with open(settings_filepath, 'w') as json_file:
            json.dump(settings_details, json_file)

    @classmethod
    def change_language_on_settings_file(cls, lang) -> None:
        """
        Updates the language setting in the application's settings file.

        This class method reads the current settings, modifies the language entry to the
        specified value, and saves the updated settings back to the file.

        :param cls: The class that calls this method.
        :type cls: type
        :param lang: The new language to be set, represented as a Language enum.
        :type lang: Language

        :return: None

        :raises FileNotFoundError: If the settings file does not exist.
        :raises json.JSONDecodeError: If there is an error reading the settings file.
        :raises IOError: If there is an error writing to the settings file.

        :example:
            Settings.change_language_on_settings_file(Language.ENGLISH)
        """

        work_dir_path = ProgramFileStructure.get_otl_wizard_work_dir()
        settings_file = work_dir_path / cls.settings_filename
        with open(settings_file) as json_file:
            settings_details = json.load(json_file)
        settings_details['language'] = str(lang.name)
        with open(settings_file, 'w') as f:
            json.dump(settings_details, f)

    @classmethod
    def get_language_from_settings(cls) -> Language:
        """
        Retrieves the current language setting from the application's settings file.

        This class method reads the settings file and returns the language specified within it as
        a Language enum.

        :return: The language currently set in the settings file.
        :rtype: Language

        :raises FileNotFoundError: If the settings file does not exist.
        :raises json.JSONDecodeError: If there is an error reading the settings file.
        :raises KeyError: If the 'language' key is not found in the settings details.

        :example:
            current_language = Settings.get_language_from_settings()
        """

        work_dir_path = ProgramFileStructure.get_otl_wizard_work_dir()
        settings_file = work_dir_path / cls.settings_filename
        with open(settings_file) as json_file:
            settings_details = json.load(json_file)
        return Language[settings_details['language']]

    @classmethod
    def load_settings(cls,settings_filepath:Path):
        try:
            with open(settings_filepath, 'r') as json_file:
                return json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}