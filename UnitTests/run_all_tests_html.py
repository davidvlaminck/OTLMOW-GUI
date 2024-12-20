import os
import pathlib
import webbrowser

import pytest

os.chdir(pathlib.Path.cwd())

if __name__ == "__main__":
    # to test a single file
    # pytest.main(['--cov', '-v', 'project_files_test/ProjectFileManager_test.py', '--cov-report=html'])
    pytest.main(['--cov', '-v', '--cov-report=html','--cov-config=C:\\Users\\chris\\PycharmProjects\\OTLMOW-GUI\\UnitTests\\.coveragerc'])
    webbrowser.open_new_tab(str(pathlib.Path('htmlcov/index.html')))
