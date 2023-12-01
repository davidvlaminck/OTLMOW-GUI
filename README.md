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

## Installation guide
Currently, you need at least Python version 3.8 to use this library.

To install the OTL MOW project into your Python project, use pip to install it:
``` 
pip install otlmow_gui
```
To upgrade an existing installation use:
``` 
pip install otlmow_gui --upgrade
```
Then you can run the main.py to see the GUI in action.

We are working on a way to deploy this to the different operating systems. This is expected near the end of 2023.
