import pathlib
import shutil

import PyInstaller.__main__

home_path = pathlib.Path.home()

PyInstaller.__main__.run([
    r'OTLWizard.py',
    '--distpath', str(home_path / 'PycharmProjects'/ 'OTLMOW-GUI' /  'LatestRelease'),
    '--contents-directory', 'applicationdata',
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
    '--icon','img/wizard.png',
    '--noconfirm',
    '--onefile',  # All files packed together in one executable file
    '--noconsole', # no cmd/powershell window with debug output
    '--clean'
])

# TODO: make sure custom.qss and demo projects are copied next to .exe > verify it is loaded same as locale