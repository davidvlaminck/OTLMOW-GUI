import pathlib
import shutil

import PyInstaller.__main__

home_path = pathlib.Path.home()

PyInstaller.__main__.run([
    r'OTL Wizard 2.py',
    '--distpath', str(home_path / 'PycharmProjects'/ 'OTLMOW-GUI' /  'LatestReleaseMulti'),
    '--contents-directory', 'data',
    '--paths', str(home_path / 'PycharmProjects' / 'OTLMOW-GUI' / 'venv3-13' / 'Lib' / 'site-packages'),
    '--collect-all', 'otlmow_converter',
    '--collect-all', 'otlmow_model',
    '--collect-all', 'otlmow_template',
    '--collect-all', 'otlmow_modelbuilder',
    '--collect-all', 'otlmow_visuals',
    '--collect-all', 'pyvis',
    '--add-data', 'locale:locale',
    '--add-data', 'style:style',
    '--add-data', 'demo_projects:demo_projects',
    '--add-data', 'img:img',
    '--add-data', 'pyproject.toml:.',
    '--icon','img/wizard.png',
    '--splash','img/wizard1.png',
    '--noconfirm',
    # '--onefile',  # All files packed together in one executable file
    '--noconsole', # no cmd/powershell window with debug output
    '--clean'
])

# TODO: make sure custom.qss and demo projects are copied next to .exe > verify it is loaded same as locale