import os
import stat
import shutil
import subprocess
import webbrowser
from typing import NamedTuple

from github import GithubException

from Exceptions.exceptions import GithubNotCreated, ProjectAlreadyCreated, RepoNotExists, GitHubNotSetup, DriveNotSetup, \
    FolderNotExists, ZipNotCreated

from templates.utils import get_random_id, delete_records, save_records, update_record
from google_drive.drive import upload_zip, delete_zip
from config import config, ProjectType


class ProjectCreator:
    def __init__(self, folder_name: str, project_type: ProjectType, root_path: str, files_to_create: list):
        self.project_type = project_type
        self.root_path = root_path
        self.folder_name = folder_name
        self.folder_name_path = "_".join([i for i in self.folder_name.split(" ")])
        self.project_path = self.__create_project(self.folder_name_path)
        self.files = files_to_create
        self.github_info = None
        self.virtual_env = False
        self.__create_files()
        self.id = get_random_id()
        self.save_project(config.DB_NAME)
        self.completed = False
        self.zip_info = None

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
        if self.files and isinstance(self.files, list):
            for file in self.files:
                path = os.path.join(self.project_path, file)
                open(path, 'w').close()

    def open_project_folder(self):
        subprocess.run(f"explorer {self.project_path}")

    def open_folder_in_pycharm(self):
        subprocess.run(["powershell.exe", "pycharm64.exe", f"\"{self.project_path}\""])

    def delete_project(self, db_name, github_profile):
        if self.github_info and not github_profile:
            raise GitHubNotSetup()
        else:
            self.delete_github(github_profile)
        shutil.rmtree(self.project_path, onerror=self.__remove_readonly)
        delete_records(db_name, self.id)

    # GitHub section
    def delete_github(self, github_profile):
        if self.github_info:
            try:
                repo = github_profile.get_user().get_repo(self.github_info.repo_name)
                print('deleting repo')
                repo.delete()
                self.github_info = None

            except RepoNotExists:
                pass

    def create_github(self, repo_name, github_profile, private=False):
        user = github_profile.get_user()
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

    def delete_env(self):
        try:
            if self.virtual_env:
                bat_file = os.path.join('bin', 'delete_env.bat')
                subprocess.run([f'{bat_file}', self.project_path[0], f"{self.project_path}"])
                self.virtual_env = False

            else:
                pass

        except subprocess.CalledProcessError as e:
            print(e)

    def dump_to_drive(self, github_profile, credentials_path):
        """delete the folder from local drive, delete any GitHub linked to it, and dump it into the Google Drive in
        zip format."""
        main_folder_path = config.get_config("ROOT_DIRECTORY", "main_dir")
        if self.github_info and not github_profile:
            raise GitHubNotSetup()
        else:
            self.delete_github(github_profile)

        if not config.check_drive(credentials_path):
            raise DriveNotSetup()

        if not main_folder_path:
            raise FolderNotExists()

        if self.virtual_env:
            self.delete_env()

        zip_path = os.path.join(os.getcwd(), os.path.basename(self.folder_name_path))
        zip_created_path = self.create_zip(self.project_path, zip_path)
        if not os.path.exists(zip_created_path):
            raise ZipNotCreated()

        zip_info = upload_zip(zip_created_path, credentials_path)
        if zip_info.zip_id:
            self.zip_info = zip_info
            os.remove(zip_created_path)
            update_record(config.DB_NAME, self.id, self)

    def delete_zip_from_drive(self, credentials_path):
        if not self.zip_info.zip_id:
            raise ZipNotCreated()

        if not config.check_drive(credentials_path):
            raise DriveNotSetup()

        if delete_zip(self.zip_info.zip_id, credentials_path):
            return True


    @staticmethod
    def create_zip(dir_path, zip_path):
        if os.path.exists(dir_path):
            zp = shutil.make_archive(zip_path, "zip", dir_path)

            return zp


    def save_project(self, db_name):
        save_records(db_name, self, self.id)

class GithubInfo(NamedTuple):
    repo_url: str = None
    repo_id: int = None
    clone_url: str = None
    repo_name: str = None

