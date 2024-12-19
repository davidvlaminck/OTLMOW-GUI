import datetime
import gettext
import json
import logging
import platform
from pathlib import Path

from Domain.enums import Language
from Domain.project.ProgramFileStructure import ProgramFileStructure


class Settings:
    settings_filename = 'settings.json'

    @classmethod
    def return_language(cls,locale_dir: Path, language: Language = None):
        """
        Sets the application's language by loading the appropriate translation files.
        This class method retrieves the translation for the specified language from the
        given locale directory, defaulting to Dutch if no language is provided.

        Args:
            locale_dir (Path): The directory where the translation files are located.
            language (Language, optional): The language to be set for translations. If not provided, defaults to Language.DUTCH.

        Returns:
            function: A gettext function that can be used to translate messages.

        Raises:
            Exception: If there is an error loading the translation files.

        Examples:
            translator = Settings.return_language(Path('/path/to/locales'), Language.ENGLISH)
        """

        logging.debug(f"Changing language to: {str(language)}")
        if language is None:
            language = Language.DUTCH
        translator = gettext.translation('messages', localedir=locale_dir, languages=[language.value])
        translator.install()
        return translator.gettext

    @classmethod
    def get_or_create_settings_file(cls) -> None:
        """
        Retrieves or creates a settings file for the application.
        This class method checks for the existence of a settings file and initializes
        it with default values if it does not exist, including the operating system,
        language, and run timestamps.

        Args:


        Returns:
            dict: A dictionary containing the settings details, including language, operating system, first run status, and last run timestamp.

        Raises:
            IOError: If there is an error reading or writing the settings file.

        Examples:
            settings = Settings.get_or_create_settings_file()
        """

        work_dir_path = ProgramFileStructure.get_otl_wizard_work_dir()
        settings_filepath = work_dir_path / 'settings.json'

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        first_run = False
        operating_sys = platform.system()
        language = Language.DUTCH
        if not settings_filepath.exists():
            first_run = True

        with open(settings_filepath, 'w+') as json_file:
            try:
                settings_details = json.load(json_file)
            except:
                settings_details = {}

            if settings_details.__contains__('language'):
                settings_details['language'] = Language[settings_details['language']]
            else:
                settings_details['language'] = str(language.name)

            settings_details['OS'] = str(operating_sys)
            settings_details['first_run'] = first_run
            settings_details['last_run'] = timestamp

            json.dump(settings_details, json_file)

            return settings_details

    @classmethod
    def change_language_on_settings_file(cls, lang) -> None:
        """
        Updates the language setting in the application's settings file. This class method reads the current settings, modifies the language entry to the specified value, and saves the updated settings back to the file.

        :param cls: The class that calls this method.
        :param lang: The new language to be set, represented as a Language enum.

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
        This class method reads the settings file and returns the language specified within it
        as a Language enum.

        Args:


        Returns:
            Language: The language currently set in the settings file.

        Raises:
            FileNotFoundError: If the settings file does not exist.
            json.JSONDecodeError: If there is an error reading the settings file.
            KeyError: If the 'language' key is not found in the settings details.

        Examples:
            current_language = Settings.get_language_from_settings()
        """

        work_dir_path = ProgramFileStructure.get_otl_wizard_work_dir()
        settings_file = work_dir_path / cls.settings_filename
        with open(settings_file) as json_file:
            settings_details = json.load(json_file)
        return Language[settings_details['language']]