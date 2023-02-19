import os
import pickle
from enum import Enum
from typing import Optional

import tomli_w

from github import Github, GithubException

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # noqa

from Exceptions.exceptions import GitHubNotSetup, DriveNotSetup, FolderNotExists

DB_NAME = 'db.pickle'
CONFIG_FILE_NAME = "config.toml"

class ProjectType(Enum):
    Coding_Problems = "Coding_Problems"
    Fun_Personal = "Fun_Personal"
    Learning = "Learning"
    Progress = "Progress"
    Professional_Projects = "Professional_Projects"

class Config:
    config_file_path = os.path.join(os.getcwd(), CONFIG_FILE_NAME)

    def get_config(self, *args) -> Optional[dict]:
        if os.path.exists(self.config_file_path):
            with open(self.config_file_path, 'rb') as fp:
                data = tomllib.load(fp)
                try:
                    if len(args) == 2:
                        return data.get(args[0]).get(args[1])
                    elif len(args) == 1:
                        return data.get(args[0])
                    else:
                        return data

                except AttributeError:
                    raise FolderNotExists("No folder exists")
        return None

    @staticmethod
    def __get_token(github_token, env_var):
        if github_token and env_var:
            os.environ[env_var] = github_token
            token = github_token
        elif not env_var and github_token:
            os.environ['github_token'] = github_token
            token = github_token
        elif not github_token and env_var:
            token = os.environ[env_var]
        else:
            token = os.environ["github_token"]

        return token

    def __check_github(self, github_token, env_var):
        token = self.__get_token(github_token, env_var)
        if self.__token_validation(token):
            return True
        return False

    @staticmethod
    def __token_validation(token):
        gh = Github(token)
        try:
            gh.get_user()
            return True
        except GithubException:
            return False

    def setup_config_path(self, path, folder_name, github_token, env):
        if not os.path.exists(os.path.join(os.getcwd(), "google_drive", "credentials.json")):
            raise DriveNotSetup()

        if not self.__check_github(github_token, env):
            raise GitHubNotSetup()

        with open(self.config_file_path, 'wb') as f:
            config = {}
            try:
                if ":" not in path:
                    path += ":\\"
                root_dir = os.path.join(path, folder_name)
                os.mkdir(root_dir)
                config["ROOT_DIRECTORY"] = {"main_dir": root_dir}
                sub_folders = [ProjectType.Progress.value, ProjectType.Learning.value, ProjectType.Fun_Personal.value,
                               ProjectType.Coding_Problems.value,
                               ProjectType.Professional_Projects.value]
                sfg = {}
                for sub_folder in sub_folders:
                    sub_folder_path = os.path.join(root_dir, sub_folder)
                    os.mkdir(sub_folder_path)
                    sfg[sub_folder] = sub_folder_path
                config["SUB_DIRECTORY"] = sfg

            except IOError:
                raise Exception("Unknown exception")

            config["GOOGLE_DRIVE_TOKEN"] = {"enable": True}
            config["GITHUB_TOKEN"] = {"enable": True}
            config["DB"] = {"DB_FILE_NAME": DB_NAME}

            tomli_w.dump(config, f)


config = Config()
if not os.path.exists(DB_NAME):
    with open(DB_NAME, 'wb') as f:
        pickle.dump({}, f)
