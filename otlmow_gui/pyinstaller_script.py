import os
import pathlib
import shutil
import sys

import PyInstaller.__main__

from otlmow_gui.Domain.logger.OTLLogger import OTLLogger

home_path = pathlib.Path.home()

OTLLogger.init()
OTLLogger.logger.debug("PyInstaller.__main__.run", extra={"timing_ref":"PyInstaller.__main__.run"})

root_path = pathlib.Path(__file__).parent.parent  # repo root
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
    str(root_path / 'otlmow_gui' / 'OTL Wizard 2.py'),
    '--distpath', str(root_path /  'LatestReleaseMulti'),
    '--contents-directory', 'data',
    '--paths', paths,
    '--paths', str(root_path),
    '--exclude-module','otlmow_model',
    '--collect-all', 'otlmow_converter',
    '--collect-all', 'otlmow_model',
    '--hidden-import', 'otlmow_model',
    '--collect-all', 'otlmow_template',
    '--collect-all', 'otlmow_modelbuilder',
    '--collect-all', 'otlmow_visuals',
    '--collect-all', 'pyvis',
    '--add-data', f"{str(root_path / 'otlmow_gui' / 'locale')}{sep}locale",
    '--add-data', f"{str(root_path / 'otlmow_gui' / 'style')}{sep}style",
    '--add-data', f"{str(root_path / 'otlmow_gui' / 'demo_projects')}{sep}demo_projects",
    '--add-data', f"{str(root_path / 'otlmow_gui' / 'img')}{sep}img",
    '--add-data', f"{str(root_path / 'pyproject.toml')}:.",
    '--add-data', f"{str(root_path / 'otlmow_gui' / 'javascripts_visualisation')}{sep}javascripts_visualisation",
    '--icon',f"{str(root_path / 'otlmow_gui' / 'img')}/wizard.png",
    '--splash',f"{str(root_path / 'otlmow_gui' / 'img')}/Logo-OTL_Wizard_2_no_purple_edge_V3.png",
    '--noconfirm',
    # '--onefile',  # All files packed together in one executable file
    '--noconsole', # no cmd/powershell window with debug output
    '--clean'
])

OTLLogger.logger.debug("PyInstaller.__main__.run", extra={"timing_ref":"PyInstaller.__main__.run"})

# rename dist folder
original_folder = root_path / 'LatestReleaseMulti' / 'OTL Wizard 2'
target_folder = root_path / 'LatestReleaseMulti' / 'OTL_Wizard_2'
if original_folder.exists():
    if target_folder.exists():
        shutil.rmtree(target_folder)
    shutil.move(str(original_folder), str(target_folder))
else:
    raise FileNotFoundError(f"Expected folder not found: {original_folder}")

# final executable path
exe_path = target_folder / 'OTL Wizard 2.exe'
if not exe_path.exists():
    raise FileNotFoundError(f"Executable missing: {exe_path}")
print(f"Executable at: {exe_path}")

# TODO: make sure custom.qss and demo projects are copied next to .exe > verify it is loaded same as locale