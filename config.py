import os
import pickle
from pathlib import Path
from typing import Optional

import tomli_w

from github import Github, GithubException

from google_drive.drive import get_token
from utils.projectType import ProjectType
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # noqa

from Exceptions.exceptions import FolderNotExists

DB_NAME = 'db.pickle'
CONFIG_FILE_NAME = "config.toml"


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
        else:
            return None

    @staticmethod
    def __get_token(env_var):
        try:
            token = os.environ[env_var]
            return token
        except KeyError:
            return None

    def __check_github(self, env_var):
        token = self.__get_token(env_var)
        if token and self.__token_validation(token):
            return True
        else:
            return False

    @staticmethod
    def __token_validation(token):
        gh = Github(token)
        try:
            gh.get_user()
            return True
        except GithubException:
            return False

    def setup_config_path(self, path, folder_name):
        with open(self.config_file_path, 'wb') as f:
            f = open(self.config_file_path, 'rb')
            data = tomllib.load(f)
            f.close()
            try:
                root_dir = Path(path, folder_name)
                os.mkdir(root_dir)
                data["ROOT_DIRECTORY"] = {"main_dir": root_dir}
                sub_folders = [ProjectType.Progress.value, ProjectType.Learning.value, ProjectType.Fun_Personal.value,
                               ProjectType.Coding_Problems.value,
                               ProjectType.Professional_Projects.value]
                sfg = {}
                for sub_folder in sub_folders:
                    sub_folder_path = root_dir / sub_folder
                    os.mkdir(sub_folder_path)
                    sfg[sub_folder] = sub_folder_path
                data["SUB_DIRECTORY"] = sfg
                tomli_w.dump(data, f)

            except IOError:
                raise Exception("Unknown exception")

    def setup_github(self, variable_name):
        f = open(self.config_file_path, 'rb')
        data = tomllib.load(f)
        f.close()
        with open(self.config_file_path, 'wb') as conf:
            data["GITHUB_TOKEN"]["enable"] = True
            data["GITHUB_TOKEN"]["variable_name"] = variable_name
            tomli_w.dump(data, conf)

    def setup_drive(self):
        t = get_token()
        if t:
            f = open(self.config_file_path, 'rb')
            data = tomllib.load(f)
            f.close()
            with open(self.config_file_path, 'wb') as conf:
                data["GOOGLE_DRIVE_TOKEN"]["enable"] = True
                tomli_w.dump(data, conf)
            print(t)
            return t


if not os.path.exists(DB_NAME):
    with open(DB_NAME, 'wb') as f:
        pickle.dump({}, f)

config = Config()
if not Path(config.config_file_path).exists():
    with open(config.config_file_path, 'wb') as f:
        cfg = {"GOOGLE_DRIVE_TOKEN": {"enable": False}, "GITHUB_TOKEN": {"enable": False, "variable_name": ""},
               "DB": {"DB_FILE_NAME": DB_NAME}}
        tomli_w.dump(cfg, f)

