import os
import stat
import shutil
import subprocess
import webbrowser
from typing import NamedTuple

from github import Github, GithubException

from Exceptions.exceptions import GithubNotCreated, ProjectAlreadyCreated, RepoNotExists

from utils.utils import get_random_id, delete_records, save_records, ProjectType
import config


class Base:
    github = Github(os.getenv("github_token"))
    files_to_create = ["notes.txt", "progress.md", "requirements.txt"]  # Base implementation, mutate for subclass

    def __init__(self, folder_name: str, project_type: ProjectType, root_path):
        self.project_type = project_type
        self.root_path = root_path
        self.folder_name = folder_name
        self.folder_name_path = "_".join([i for i in self.folder_name.split(" ")])
        self.project_path = self.__create_project(self.folder_name_path)
        self.file_name = "main.py"
        self.github_info = None
        self.virtual_env = False
        self.__create_files()
        self.id = get_random_id()
        self.save_project(config.DB_NAME)
        self.completed = False

    def __str__(self):
        return f"{self.folder_name}"

    # helper functions
    def __create_project(self, folder_name_path):
        path = os.path.join(self.root_path, folder_name_path)
        if os.path.exists(path):
            raise ProjectAlreadyCreated(f'project already created at: {path}')
        os.mkdir(path)

        return path

    # helper functions
    @staticmethod
    def __remove_readonly(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    # helper functions
    def __create_files(self):
        files = self.files_to_create[:]
        files.append(self.file_name)
        for file in files:
            path = os.path.join(self.project_path, file)
            open(path, 'w').close()

    def open_project_folder(self):
        subprocess.run(f"explorer {self.project_path}")

    def open_folder_in_pycharm(self):
        subprocess.run(["powershell.exe", "pycharm64.exe", f"{self.project_path}"])

    def delete_project(self, db_name):
        if self.github_info:
            self.delete_github()
        shutil.rmtree(self.project_path, onerror=self.__remove_readonly)
        delete_records(db_name, self.id)

    # GitHub section
    def delete_github(self):
        if self.github_info:
            try:
                repo = self.github.get_user().get_repo(self.github_info.repo_name)
                print('deleting repo')
                repo.delete()
                self.github_info = None

            except RepoNotExists:
                pass

    def create_github(self, repo_name, private=False):
        user = self.github.get_user()
        try:
            repo = user.create_repo(
                name=repo_name,
                auto_init=True,
                private=private,
                gitignore_template="Python",
                license_template="mit",
            )
            print("repo", repo)
            self.github_info = GithubInfo(repo_url=repo.html_url, repo_id=repo.id, repo_name=repo.name,
                                          clone_url=repo.clone_url)
            bat_file = os.path.join('bin', 'create_repo.bat')
            subprocess.run([f'{bat_file}', self.project_path[0], self.project_path, repo.clone_url])

        except GithubException as e:
            print(e)
            if e.status == 401:
                raise Exception("Token Invalid!")
            if e.status == 422:
                raise Exception("Repo Already Created!")

    def open_github_link(self):
        if self.github_info:
            webbrowser.open(self.github_info.repo_url)
        else:
            raise GithubNotCreated("Github not created!")

    # env section
    def create_env(self):
        try:
            if not self.virtual_env:
                bat_file = os.path.join('bin', 'create_env.bat')
                subprocess.run([f'{bat_file}', self.project_path[0], f"{self.project_path}"])
                self.virtual_env = True
            else:
                pass

        except subprocess.CalledProcessError as e:
            print(e)

    def dump_to_drive(self):  # UNFINISHED
        """delete the folder from local drive, delete any GitHub linked to it, and dump it into the Google Drive in
        zip format."""
        # FIXIT: WILL ADD LATER
        pass

    def save_project(self, db_name):
        save_records(db_name, self, self.id)

class GithubInfo(NamedTuple):
    repo_url: str = None
    repo_id: int = None
    clone_url: str = None
    repo_name: str = None
