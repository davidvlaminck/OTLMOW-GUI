# OTLMOW-GUI
[![PyPI](https://img.shields.io/pypi/v/otlmow-gui?label=latest%20release)](https://pypi.org/project/otlmow-gui/)
[![otlmow-gui-downloads](https://img.shields.io/pypi/dm/otlmow-gui)](https://pypi.org/project/otlmow-gui/)
[![Unittests](https://github.com/davidvlaminck/OTLMOW-GUI/actions/workflows/unittest.yml/badge.svg)](https://github.com/davidvlaminck/OTLMOW-GUI/actions/workflows/unittest.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/otlmow-gui)
[![GitHub issues](https://img.shields.io/github/issues/davidvlaminck/OTLMOW-GUI)](https://github.com/davidvlaminck/OTLMOW-GUI/issues)
[![coverage](https://github.com/davidvlaminck/OTLMOW-GUI/blob/master/UnitTests/coverage.svg)](https://htmlpreview.github.io/?https://github.com/davidvlaminck/OTLMOW-GUI/blob/master/UnitTests/htmlcov/index.html)


## Summary
The main use case of the otlmow-gui is to provide a graphical user interface for the OTLMOW project. It is built using the [PyQt6 framework](https://www.riverbankcomputing.com/software/pyqt/intro) and is compatible with Python 3.7 and higher. This will eventually replace the OTL wizard.

## OTLMOW Project 
This project aims to implement the Flemish data standard OTL (https://wegenenverkeer.data.vlaanderen.be/) in Python.
It is split into different packages to reduce compatibility issues
- [otlmow_model](https://github.com/davidvlaminck/OTLMOW-Model)
- [otlmow_modelbuilder](https://github.com/davidvlaminck/OTLMOW-ModelBuilder)
- [otlmow_converter](https://github.com/davidvlaminck/OTLMOW-Converter)
- [otlmow_template](https://github.com/davidvlaminck/OTLMOW-Template)
- [otlmow_postenmapping](https://github.com/davidvlaminck/OTLMOW-PostenMapping)
- [otlmow_davie](https://github.com/davidvlaminck/OTLMOW-DAVIE)
- [otlmow_visuals](https://github.com/davidvlaminck/OTLMOW-Visuals)
- [otlmow_gui](https://github.com/davidvlaminck/OTLMOW-GUI) (you are currently looking at this package)

## Install with pip
You can download install the OTL Wizard [here](https://github.com/davidvlaminck/otlmow-gui/wiki/Installation) if you're on Windows.
Or you can use a Python virtual environment on any platform, install this package and run the otlwizard command.
### Installing a virtual environment
- Make sure you have Python 3.7 or higher installed and that your python environment variable points to it.
- Create a new folder for your virtual environment and navigate to it in a terminal. 
- Create a new virtual environment with the command:
```
python -m venv venv
```
Activate the virtual environment
- On Windows:
```
venv\Scripts\activate
```
- On MacOS/Linux:
```
source venv/bin/activate
```
### Installing this package
Install the package with pip and uv:
```
pip install uv
uv pip install otlmow-gui==1.1.1rc5
```
### Run the OTL wizard command
You can now run the OTL wizard with the command:
```
otlwizard
```

## Setup development environment guide
### NEEDS atleast python 3.13.2 to use the pyinstaller_script.py to create an .exe file

Follow these steps to start working with the OTL-wizard 2 source code and run de development version  
Each step will have the required commands in a PowerShell terminal as administrator (windows) starting from an empty folder.

1. Clone this repository into a folder or use an IDE to setup a project from this repository.  
   ```
   git clone https://github.com/davidvlaminck/OTLMOW-GUI.git
   cd .\OTLMOW-GUI\ 
   ```  

2. Setup a virtual python >= 3.13.2 environment and install the requirements.txt  
   ```
   python -m venv venv # your python environment variable needs to point to a python version higher than 3.13.2
   Set-ExecutionPolicy RemoteSigned # needed to let PowerShell execute .ps scripts
   venv\Scripts\activate
   python --version #shows the version of your python check if it is >3.13.2
   pip install -r requirements.txt
   ```  

3. (SKIPABLE) To use de SDF-file functionality (only windows) install the FDO Toolbox, you can find the installer in this 
    repository at:  
    ```
    LatestReleaseMulti/additional_programs/FDOToolbox-Release-v1.5.3-x64-Setup.exe
    ```


4. To run the OTL wizard 2 open a terminal in de root of the project and activate your virtual environment,  
then run the following:
    ```
    python "OTL Wizard 2.py"
    ```
    
## exe and installer creation guide

Follow these steps (NOT PowerShell commands) to create a new executable of OTL Wizard 2 and a new installer. These are ready for distribution then.

1. Make sure you have a python 3.13 environment with the requirements.txt installed set up, see [Setup development environment guide](#Setup-development-environment-guide)  
    NOTE: Keep using PyInstaller 6.10.0, newer version can get [false positives](https://github.com/pyinstaller/pyinstaller/issues/5854) on Windows Defender. Lookout for detections of 
    Wacatac.B!ml, Wacatac.H!ml, Wacapew.C!ml these are false positives. 
    They get detected only when you compile with newer versions and not when you compile with older versions of PyInstaller.
    If any user has a detection, it is most likely because of an outdated Windows Defender. Ask them to update Windows and/or Windows Defender.  
  

2. To change the version number of OTL Wizard 2, you need to change two version variables.  
   These are:  
    variable `version = "<your_version_number>"` in `pyproject.toml`  
    variable `#define MyAppVersion "<your_version_number>"` in `LatestReleaseMulti/inno_setup_installer_setup_script.iss`  
  

3. Run the `pyinstaller_script.py` in that environment.  
    This will make the file:`LatestReleaseMulti/OTL Wizard 2/OTL Wizard 2.exe`  
    and accompanying folder:`LatestReleaseMulti/OTL Wizard 2/data`
  

4. Sign the `LatestReleaseMulti/OTL Wizard 2/OTL Wizard 2.exe` file with windows [signtool](https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool) to get this signtool you need to install the [windows SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/)  
   Get a certificate from the Vlaamse Overheid or Agentschap Wegen en Verkeer.  
   Use this certificate to sign the generated exe-file with the command:  
   `C:\"Program Files (x86)"\"Windows Kits"\10\"App Certification Kit"\signtool.exe sign /f "<absolute path to certificate file>" /fd SHA256 "<absolute path to OTL Wizard 2.exe file>"`
  

5. Download and install [Inno Setup Compiler](https://jrsoftware.org/isinfo.php)
  

6. In the `LatestReleaseMulti/inno_setup_installer_setup_script.iss` script replace the MyAppDevRoot variable with the absolute path to the root of your project (the folder with the `pyproject.toml` in)  
  In the Inno Setup Compiler interface the compile button is here:  
  ![inno_setup_compile_button](compile_button_in_inno_setup.png)  


7. Open `LatestReleaseMulti/inno_setup_installer_setup_script.iss` with Inno Setup Compiler and compile.  
    This should create `LatestReleaseMulti/OTL wizard 2 installer V<version>.exe`
  

8. Sign the `LatestReleaseMulti/OTL wizard 2 installer V<version>.exe` file with windows [signtool](https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool) from step 3
   Use the same certificate from the Vlaamse Overheid or Agentschap Wegen en Verkeer as that from step 3.  
   Use this certificate to sign the generated installer exe-file with the command:  
   `C:\"Program Files (x86)"\"Windows Kits"\10\"App Certification Kit"\signtool.exe sign /f "<absolute path to certificate file>" /fd SHA256 "<absolute path to OTL wizard 2 installer V<version>.exe file>"`
  

9. To make the zipped version (no install needed).  
    Place the following files and folders into a folder and zip it preferrably with the foldername: `OTL Wizard 2 V<your version number>`:   
    File:`LatestReleaseMulti/OTL Wizard 2/OTL Wizard 2.exe`  (preferrably rename it to `OTL Wizard 2 V<your version number>.exe`)  
    Folder:`LatestReleaseMulti/OTL Wizard 2/data`  
    Folder:`LatestReleaseMulti/additional_programs`  
    The zip should look like this:  
    ![zip_contents_example.png](zip_contents_example.png)
  

10. Until V1.1 publishing to the wider audience is done by placing both the zip and installer-exe file in folder `LatestRelease` 
    and push to or merge into the master branch of this repository (OTLMOW-GUI) (needs permission from repository owner)  

## Translations guide

This guide is for when you want to change translations in the program or if you are adding text that needs translations  

The easiest way to add translations to the code is by using the code: `GlobalTranslate._("<new text that needs translating>")`  
In most screen classes however you can use `self._("<new text that needs translating>")`  
These functions will return the translation for the given text

For more info on how the translations are applied in the code look at the [babel documentation](https://babel.pocoo.org/en/latest/api/core.html)  

Follow these steps (MOST are PowerShell commands) to add/change translations:

1. Install babel in the python environment 
    `pip install babel`  


2. Generate the locale\base.pot file from the strings (those in `_(<to_be_extracted_string>)`) in your python code by running:  
    `pybabel extract -F babel.cfg -o locale\base.pot .\Domain .\GUI .\Exceptions`  
  

2. Update the `locale\\<language_code>\LC_MESSAGES\message.po` files to the new base.pot with:  
    `pybabel update -i .\locale\base.pot -d locale --no-fuzzy-matching`  


3. Find your `new_text_key` in the `locale\\<language_code>\LC_MESSAGES\message.po` of each language and fill in the
tranlation for that text in like:
    ```
    msgid "new_text_key"
    msgstr "The translation for this new key"
    ```
   if you don't know all the text_keys you added you can search for `msgstr ""` to find all msgids that have no translation yet
  

4. Compile new translations into messages.mo files 
    `pybabel compile -d locale`
    
## Custom logging implementation usage

This project has a custom logging class called OTLLogger.py, it is build on the standard logging library.  
Instead of using `logging.debug("message")` you should use `OTLLogger.logger.debug("message")`
  
This custom logger can also display the time between 2 `OTLLogger.logger.debug()` calls by adding the same `timing_ref` 
to the extra argument in both log calls. Example:  
```
OTLLogger.logger.debug(f"Execute OtlmowConverter.from_file_to_objects({file_path.name})", 
                            extra={"timing_ref": f"file_to_objects_{file_path.stem}"})

object_lists = list(OtlmowConverter.from_file_to_objects(file_path,**kwargs))

OTLLogger.logger.debug(f"Execute OtlmowConverter.from_file_to_objects({file_path.name}) ({len(object_lists)} objects)", 
                            extra={"timing_ref": f"file_to_objects_{file_path.stem}"})
```

## The sleeping cat GIF link
https://giphy.com/gifs/xUA7aZtd2GIfzYDR5e
