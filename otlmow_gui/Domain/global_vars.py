import os
import sys
from pathlib import Path
from typing import Optional

test_mode = False

projects = []
current_project = None
otl_wizard = None


# SDF files are only supported in Windows systems
if "win" in sys.platform:
    supported_file_formats = {'Excel':"xlsx", 'CSV':"csv", 'JSON':'json','GeoJSON': 'geojson','SDF':'sdf'}
else:
    supported_file_formats = {'Excel': "xlsx", 'CSV': "csv", 'JSON': 'json', 'GeoJSON': 'geojson'}

external_toegekendDoor_label = "OTL_wizard_2"
last_subset_selected_dir: Optional[Path] = None
FDO_toolbox_path_str =  'C:\\Program Files\\FDO Toolbox\\FdoCmd.exe'
FDO_toolbox_installer_path_str =  str(Path(os.getcwd()) / "additional_programs" / "FDOToolbox-Release-v1.5.3-x64-Setup.exe")

def get_start_dir_subset_selection(input_subset_str:str) -> Optional[str]:
    if input_subset_str:
        return os.path.dirname(input_subset_str)
    elif last_subset_selected_dir:
        return last_subset_selected_dir
    else:
        return None
