import os
import sys
from pathlib import Path

import PySimpleGUI as sg

from utils.utils import check_folder_malformed, __get_project, checkGithub
from utils.projectType import ProjectType
from utils.frontend_utils import create_project

from Exceptions.exceptions import ProjectAlreadyCreated
from windows import main_window, toggle_btn_on, toggle_btn_off
from config import config, DB_NAME


sg.theme("LightBlue2")

ENV_PERMISSION = False
GITHUB_PERMISSION = False

CHECK_SETTINGS_CREATED = config.get_config()

github_profile = checkGithub()
window = main_window()

while True:
    event, value = window.read(timeout=400)
    if event in (sg.WINDOW_CLOSED, "Cancel"):
        break

    #####-------------------- setting section ------------------#####
    if event == "PATH_SETUP":
        if not value["SETTINGS_PATH"] or not value["SETTINGS_FOLD"]:
            sg.popup_error("Drive or Folder name missing")
        else:
            if not Path(value["SETTINGS_PATH"]).exists():
                sg.popup_error("path not exists")
                continue
            path, folder = value['SETTINGS_PATH'], value["SETTINGS_FOLD"]
            config.setup_config_path(path, folder)
            window.close()
            window = main_window()
            CHECK_SETTINGS_CREATED = True

    if event == "DRIVE_SETUP":
        sg.popup_auto_close("complete the workflow to download google drive credentials.")
        config.setup_drive()
        sg.popup_ok("restart needed, run the program again")
        os.execv(sys.argv[0], sys.argv)

    if event == "SAVE_GITHUB":
        if not value["SETTINGS_ENV"]:
            sg.popup_error("Provide env variable for github token")
        else:
            env = value['SETTINGS_ENV']
            github_status = config.__check_github(env)
            if not github_status:
                sg.popup_error(f"Either token is expired or no token exists in variable {env}")
                continue
            config.setup_github(env)
            sg.popup_ok("restart needed, run the program again")
            os.execv(sys.argv[0], sys.argv)


    ####------------------------ security check ------------------------####
    if not check_folder_malformed(config) and CHECK_SETTINGS_CREATED:
        sg.popup_error("Folder are deleted or changed, please create or change manually according to the config.")
        break

    #####------------------- create project section -------------------#####
    if event == "-TOGGLE-ENV-":
        ENV_PERMISSION = not ENV_PERMISSION
        window['-TOGGLE-ENV-'].update(image_data=toggle_btn_on if ENV_PERMISSION else toggle_btn_off)
    if event == "-TOGGLE-GITHUB-":
        GITHUB_PERMISSION = not GITHUB_PERMISSION
        window['-TOGGLE-GITHUB-'].update(image_data=toggle_btn_on if GITHUB_PERMISSION else toggle_btn_off)

    if event == '-CREATE-PROJECT-':
        if not CHECK_SETTINGS_CREATED:
            sg.popup_error("no settings found. go to settings tab and manage settings.")
        else:
            if not value["-FOLDER_NAME-"]:
                sg.popup_error("Values missing!")
                continue
            if value['-TEMPLATE-'] == "Select Template":
                sg.popup_error("Select Template")
                continue
            if not github_profile and GITHUB_PERMISSION:
                sg.popup_error("Github not set up!")
                continue
            if GITHUB_PERMISSION and not value["-REPO_NAME-"]:
                sg.popup_error("Enter Repo Name!")
                continue

            template = next(i for i in ProjectType if i.value == value['-TEMPLATE-'])
            project_name = value["-FOLDER_NAME-"]
            repo_name = value["-REPO_NAME-"]
            try:
                root_path = config.get_config("SUB_DIRECTORY", template.value)
                window.perform_long_operation(lambda: create_project(project_name, ENV_PERMISSION, GITHUB_PERMISSION,
                                repo_name, template, root_path, github_profile), end_key="-CREATE_PROJECT_COMPLETED-")

            except ProjectAlreadyCreated:
                sg.popup_error("Project Already Created!")
                continue

            sg.popup_auto_close("this will take a moment to create please wait!")
            window["-CREATE-PROJECT-"].update(disabled=True)

    #####---------------- project related events ------------------#####
    if event == "-CREATE_PROJECT_COMPLETED-":
        sg.popup_auto_close("Project Created!")
        window.close()
        window = main_window()

    if "OIP_" in event:  # Open In Ide
        instance = __get_project(event)
        instance.open_folder_in_pycharm()

    if "OPF_" in event:  # Open Folder
        instance = __get_project(event)
        instance.open_project_folder()

    if "DP_" in event:  # Del Project
        if sg.popup_ok_cancel("Are you sure you want to delete project?") == "OK":
            instance = __get_project(event)
            instance.delete_project(DB_NAME, github_profile)
            window.close()
            window = main_window()

    if "OGL_" in event:  # Open Github Link
        instance = __get_project(event)
        instance.open_github_link()

window.close()
