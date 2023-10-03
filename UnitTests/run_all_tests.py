import os, pathlib
import pytest

os.chdir(pathlib.Path.cwd())

if __name__ == "__main__":
    pytest.main(['--cov', '-v'])
