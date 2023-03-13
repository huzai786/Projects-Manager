import os
import pickle
import shutil
from pathlib import Path

import tomli_w

from github import Github, GithubException
from enum import Enum

from google_drive.drive import get_token, drive_folder
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # noqa


CONFIG_FILE_NAME = "config.toml"




class Config:
    config_file_path = os.path.join(os.getcwd(), CONFIG_FILE_NAME)
    DB_NAME = 'db.pickle'

    def get_config(self, *args):
        if os.path.exists(self.config_file_path):
            with open(self.config_file_path, 'rb') as fp:
                data = tomllib.load(fp)
                try:
                    if len(args) == 2:
                        value: str = data.get(args[0]).get(args[1])
                        return value
                    elif len(args) == 1:
                        return data.get(args[0])
                    else:
                        return data

                except AttributeError:
                    return None
        else:
            return None

    def setup_config_path(self, path, folder_name):
        fr = open(self.config_file_path, 'rb')
        data = tomllib.load(fr)
        fr.close()
        with open(self.config_file_path, 'wb') as fw:
            try:
                root_dir = Path(path, folder_name)
                os.mkdir(root_dir)
                data["ROOT_DIRECTORY"] = {"main_dir": str(root_dir)}
                for name, path in data["SUB_DIRECTORY"].items():
                    sub_folder_path = root_dir / name
                    os.mkdir(sub_folder_path)
                    data["SUB_DIRECTORY"][name] = str(sub_folder_path)
                tomli_w.dump(data, fw)

            except IOError:
                raise Exception("Unknown exception")

    def delete_all_folders(self):
        p = self.get_config("ROOT_DIRECTORY", "main_dir")
        if p:
            shutil.rmtree(p)
            os.remove(self.DB_NAME)
            self.update_config("", "ROOT_DIRECTORY", "main_dir")
            for i in ProjectType:
                self.update_config("", "SUB_DIRECTORY", i.value)

    def update_config(self, value, *args):
        fr = open(self.config_file_path, 'rb')
        data = tomllib.load(fr)
        fr.close()
        with open(self.config_file_path, 'wb') as fw:
            try:
                if len(args) == 2:
                    data[args[0]][args[1]] = value
                    tomli_w.dump(data, fw)
                else:
                    return None

            except IOError:
                raise Exception("Unknown exception")

    def save_github_token(self, variable_name):
        f = open(self.config_file_path, 'rb')
        data = tomllib.load(f)
        f.close()
        with open(self.config_file_path, 'wb') as conf:
            data["GITHUB_TOKEN"]["enable"] = True
            data["GITHUB_TOKEN"]["variable_name"] = variable_name
            tomli_w.dump(data, conf)

    def save_drive_settings(self, credential_file_path):
        cre_path = Path(credential_file_path)
        token = get_token(cre_path)
        if token:
            f = open(self.config_file_path, 'rb')
            data = tomllib.load(f)
            f.close()
            destination_file = Path.cwd() / drive_folder / cre_path.name
            if not destination_file.exists():
                shutil.copy(cre_path, destination_file)
            with open(self.config_file_path, 'wb') as conf:
                data["GOOGLE_DRIVE_TOKEN"]["enable"] = True
                data["GOOGLE_DRIVE_TOKEN"]["credential_path"] = str(destination_file)
                tomli_w.dump(data, conf)
            print(token)
            return True
        return False

    def check_folder_malformed(self):
        cfg = self.get_config()
        dirs = [cfg['ROOT_DIRECTORY'].get("main_dir")] + [v for k, v in cfg['SUB_DIRECTORY'].items()]
        for d in dirs:
            if not os.path.exists(d):
                return False
        return True

    def check_settings_created(self):
        if os.path.exists(self.config_file_path):
            with open(self.config_file_path, 'rb') as fp:
                data = tomllib.load(fp)
                if data["ROOT_DIRECTORY"]["main_dir"]:
                    return True
                else:
                    return False
        else:
            return False

    @staticmethod
    def __get_token(env_var):
        try:
            token = os.environ[env_var]
            return token
        except KeyError:
            return None

    def get_github_profile(self):
        var = self.get_config("GITHUB_TOKEN", "variable_name")
        if var and self.check_token_validity(var):
            g = Github(os.getenv(var))
            return g

        return None

    @staticmethod
    def check_drive(cred_path):
        if cred_path and get_token(cred_path):
            return cred_path
        else:
            return False

    def check_token_validity(self, env_var):
        token = self.__get_token(env_var)
        if token and self.__token_validation(token):
            return True
        else:
            return False

    def delete_drive_credentials(self):
        cred_path = self.get_config("GOOGLE_DRIVE_TOKEN", "credential_path")
        os.remove(cred_path)
        token_path = Path(cred_path).parent / "token.json"
        if token_path.exists():
            os.remove(token_path)

        self.update_config("", "GOOGLE_DRIVE_TOKEN", "credential_path")
        self.update_config(False, "GOOGLE_DRIVE_TOKEN", "enable")

    def add_project_types(self, type_names):
        fr = open(self.config_file_path, 'rb')
        data = tomllib.load(fr)
        fr.close()
        with open(self.config_file_path, 'wb') as fw:
            data['PROJECT_TYPE_NAMES'] = type_names
            for tn in type_names:
                data["SUB_DIRECTORY"][tn] = ""
            tomli_w.dump(data, fw)


    @staticmethod
    def __token_validation(token):
        gh = Github(token)
        try:
            gh.get_user()
            return True
        except GithubException:
            return False


if not os.path.exists(Config.DB_NAME):
    with open(Config.DB_NAME, 'wb') as f:
        pickle.dump({}, f)

config = Config()

if not Path(config.config_file_path).exists():
    with open(config.config_file_path, 'wb') as f:
        cfg = {
            "GOOGLE_DRIVE_TOKEN": {"enable": False, "credential_path": ""},
            "GITHUB_TOKEN": {"enable": False, "variable_name": ""},
            "DB": {"DB_FILE_NAME": Config.DB_NAME},
            "ROOT_DIRECTORY": {"main_dir": ""},
            "SUB_DIRECTORY": {},
            "PROJECT_TYPE_NAMES": ["type1", "type2", "type3", "type4", "typ5"]
        }
        tomli_w.dump(cfg, f)

types: list = config.get_config("PROJECT_TYPE_NAMES")
ProjectType = Enum('ProjectType', {f"Type {i}": v for i, v in enumerate(types)})
