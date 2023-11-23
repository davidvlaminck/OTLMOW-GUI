import logging
import os
from pathlib import Path
from typing import List

import requests
from github import Github, ContentFile


class GitHubDownloader:
    def __init__(self, repo_owner_and_name: str):
        self.repo_owner_and_name = repo_owner_and_name
        self.repo = Github().get_repo(repo_owner_and_name)

    def download_file(self, file_path: str, destination_dir: Path):
        contents = self.repo.get_contents(file_path)

        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
            
        # url = f'https://raw.githubusercontent.com/{self.repo_owner_and_name}/master/{file_path}'
        # resp = requests.get(url)
        # with open(destination_dir / contents.name, 'wb') as f:
        #     f.write(resp.content)

        print(f'file {contents.name} downloaded')

        # with open(destination_dir / contents.name, 'wb') as f:
        #     f.write(contents.decoded_content)

    def download(self, dir_or_file_path: str, destination_dir: Path):
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        contents = self.repo.get_contents(dir_or_file_path)

        if isinstance(contents, list) or contents.type == 'dir':
            self.download_dir(contents=contents, destination_dir=destination_dir)
        else:
            self.download_file(file_path=contents.path, destination_dir=destination_dir)

    def download_dir(self, destination_dir: Path, dir_path: str = None, contents: List[ContentFile] = None):
        if contents is None:
            contents = self.repo.get_contents(dir_path)
        for content in contents:
            if content.type == 'dir':
                self.download_dir(dir_path=content.path, destination_dir=destination_dir)
            else:
                self.download_file(file_path=content.path, destination_dir=destination_dir)
