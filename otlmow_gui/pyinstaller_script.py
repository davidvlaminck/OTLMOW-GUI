import os
import pathlib
import sys

import PyInstaller.__main__

from otlmow_gui.Domain.logger.OTLLogger import OTLLogger

home_path = pathlib.Path.home()

OTLLogger.init()
OTLLogger.logger.debug("PyInstaller.__main__.run", extra={"timing_ref":"PyInstaller.__main__.run"})

root_path = pathlib.Path(__file__).parent.parent
OTLLogger.logger.debug("root_path: " + str(root_path))
OTLLogger.logger.debug("sys.path: " + str(sys.path))

paths = None
for sys_path in sys.path:
    if 'site-packages' in sys_path:
        paths = sys_path


if not paths:
    raise FileNotFoundError("cannot find the site-packages folder")


OTLLogger.logger.debug("paths: " + paths)

sep = ';' if os.name == 'nt' else ':'

PyInstaller.__main__.run([
    r'OTL Wizard 2.py',
    '--distpath', str(root_path /  'LatestReleaseMulti'),
    '--contents-directory', 'data',
    '--paths', paths,
    '--exclude-module','otlmow_model',
    '--collect-all', 'otlmow_converter',
    '--collect-all', 'otlmow_model',
    '--hidden-import', 'otlmow_model',
    '--collect-all', 'otlmow_template',
    '--collect-all', 'otlmow_modelbuilder',
    '--collect-all', 'otlmow_visuals',
    '--collect-all', 'pyvis',
    '--add-data', f'locale{sep}locale',
    '--add-data', f'style{sep}style',
    '--add-data', f'demo_projects{sep}demo_projects',
    '--add-data', f'img{sep}img',
    '--add-data', '../pyproject.toml:.',
    '--add-data', f'javascripts_visualisation{sep}javascripts_visualisation',
    '--icon','img/wizard.png',
    '--splash','img/Logo-OTL_Wizard_2_no_purple_edge_V3.png',
    '--noconfirm',
    # '--onefile',  # All files packed together in one executable file
    '--noconsole', # no cmd/powershell window with debug output
    '--clean'
])
OTLLogger.logger.debug("PyInstaller.__main__.run", extra={"timing_ref":"PyInstaller.__main__.run"})

# TODO: make sure custom.qss and demo projects are copied next to .exe > verify it is loaded same as locale