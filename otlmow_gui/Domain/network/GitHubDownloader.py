import os
import shutil
from pathlib import Path
from typing import List

import requests
from github import Github

from otlmow_gui.Domain.logger.OTLLogger import OTLLogger


class GitHubDownloader:
    def __init__(self, repo_owner_and_name: str):
        self.repo_owner_and_name = repo_owner_and_name
        self.repo: Github | None = None

    def get_repo(self):
        """
        Retrieves the GitHub repository associated with the specified owner and name.
        If the repository has not been previously fetched, it will be retrieved from the GitHub API.

        Returns:
            Repository: The GitHub repository object.

        Raises:
            Exception: If there is an issue connecting to the GitHub API or retrieving the repository.
        """

        if self.repo is None:
            self.repo = Github().get_repo(self.repo_owner_and_name)
        return self.repo

    def download_full_repo(self, dest: Path):
        """
        Downloads a zipped version of the entire GitHub repository to a specified destination directory.
        It ensures that the destination directory exists before saving the downloaded file.

        Args:
            dest (Path): The directory where the zipped repository will be saved.

        Returns:
            None

        Raises:
            OSError: If the destination directory cannot be created or accessed.
        """
        dest_filename = 'full_repo_download.zip'
        dest_dir = dest.parent / dest.stem
        #dest can be a directory or a zip file
        if dest.suffix == ".zip":
            dest_dir = dest.parent
            dest_filename = dest.name

        if  os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)
        os.makedirs(dest_dir)

        dest = dest_dir / dest_filename
        OTLLogger.logger.info(f"Download otlmow-model to zip: {dest}",extra={"timing_ref":"download_otlmow_model"})

        download_zip_url = f'https://github.com/{self.repo_owner_and_name}/zipball/master'
        resp = requests.get(download_zip_url)

        with open(dest, 'wb') as f:
            f.write(resp.content)
        OTLLogger.logger.info("Download otlmow-model to zip",
                              extra={"timing_ref": "download_otlmow_model"})

    def download_file_to_dir(self, file_path: str, destination_dir: Path, contents=None):
        """
        Downloads a file from a GitHub repository and saves it to a specified directory.
        If the file contents are not provided, it retrieves them from the repository.

        Args:
            destination_dir (Path): The directory where the downloaded file will be saved.
            file_path (str, optional): The path of the file in the repository. Defaults to None.
            contents (optional): The contents of the file to be downloaded. If None, it will be fetched from the repository.

        Returns:
            None

        Raises:
            OSError: If the destination directory cannot be created or accessed.
        """

        if contents is None:
            contents = self.get_repo().get_contents(file_path)

        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        url = f'https://raw.githubusercontent.com/{self.repo_owner_and_name}/master/{file_path}'
        resp = requests.get(url)
        with open(destination_dir / contents.name, 'wb') as f:
            f.write(resp.content)

    def download(self, dir_or_file_path: str, destination_dir: Path):
        """
        Downloads a file or directory from a GitHub repository to a specified destination directory.
        It checks the type of the contents and delegates the download process accordingly.

        Args:
            dir_or_file_path (str): The path of the file or directory in the repository to be downloaded.
            destination_dir (Path): The directory where the downloaded content will be saved.

        Returns:
            None

        Raises:
            OSError: If the destination directory cannot be created or accessed.
        """

        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        contents = self.get_repo().get_contents(dir_or_file_path)

        if isinstance(contents, list) or contents.type == 'dir':
            self.download_dir(None, destination_dir=destination_dir, contents=contents)
        else:
            self.download_file_to_dir(None, destination_dir=destination_dir, contents=contents)

    def download_dir(self, dir_path: str, destination_dir: Path, contents: List = None):
        """
        Downloads all files and subdirectories from a specified directory in a GitHub repository to a local destination.
        It recursively processes each item, ensuring that directories are handled appropriately.

        Args:
            destination_dir (Path): The directory where the downloaded contents will be saved.
            dir_path (str, optional): The path of the directory in the repository to be downloaded. Defaults to None.
            contents (List, optional): A list of contents to download. If None, it will be fetched from the repository.

        Returns:
            None

        Raises:
            OSError: If the destination directory cannot be created or accessed.
        """
        if contents is None:
            contents = self.get_repo().get_contents(dir_path)
        for content in contents:
            if content.type == 'dir':
                self.download_dir(dir_path=content.path, destination_dir=destination_dir)
            else:
                self.download_file_to_dir(file_path=content.path, destination_dir=destination_dir)

    def download_file_to_memory(self, file_path: str = None):
        """
        Downloads a file from a GitHub repository and returns its contents in memory.
        It raises an error if the file cannot be accessed, ensuring that only successful downloads are processed.

        Args:
            file_path (str, optional): The path of the file in the repository to be downloaded. Defaults to None.

        Returns:
            bytes: The contents of the downloaded file.

        Raises:
            ConnectionRefusedError: If the file cannot be accessed due to a connection issue.
        """

        url = f'https://raw.githubusercontent.com/{self.repo_owner_and_name}/master/{file_path}'
        OTLLogger.logger.info(f"Downloading file from {url}")
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            raise ConnectionRefusedError()

        return resp.content