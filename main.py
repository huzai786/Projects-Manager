import datetime
import os.path
import sys
import time
from pathlib import Path

import PySimpleGUI as sg

from config import config
from utils.utils import get_project, create_zip, upload_existing_project
from utils.project_type import ProjectType
from utils.create_project import create_project
from google_drive.drive import upload_zip

from Exceptions.exceptions import ProjectAlreadyCreated, DriveNotSetup, GitHubNotSetup
from utils.windows import main_window, toggle_btn_on, toggle_btn_off, existing_upload_window, edit_project_window

sg.theme("LightBlue2")

ENV_PERMISSION = False
GITHUB_PERMISSION = False

CHECK_SETTINGS_CREATED = config.check_settings_created()
GITHUB_PROFILE = config.get_github_profile()
EDIT_PROJECT_NAMES = False
window = main_window()

while True:
    event, value = window.read(timeout=400)
    if event in (sg.WINDOW_CLOSED, "Cancel"):
        break

    #####-------------------- setting section ------------------#####
    ###------- Path setup
    if event == "PATH_SETUP":  # when user set up path
        if not value["SETTINGS_PATH"] or not value["SETTINGS_FOLD"]:
            sg.popup_error("Drive or Folder name missing")
        else:
            if not Path(value["SETTINGS_PATH"]).exists():
                sg.popup_error("path not exists")
                continue
            path, folder = value['SETTINGS_PATH'], value["SETTINGS_FOLD"]
            config.setup_config_path(path, folder)
            sg.popup_ok("restart needed, run the program again")
            time.sleep(0.5)
            sys.exit()

    if event == "PATH_DELETE":
        if sg.popup_ok_cancel(
                "Are you sure you want to delete all the projects! make sure to sync them with google drive") == "OK":
            config.delete_all_folders()
            sg.popup_ok("restart needed")
            time.sleep(0.5)
            sys.exit()

    ###------- drive setup
    if event == "DRIVE_SETUP":
        if not value["CREDENTIALS_FILE"]:
            sg.popup_error("Select File")
        else:
            filepath = value["CREDENTIALS_FILE"]
            try:
                if config.save_drive_settings(filepath):
                    sg.popup_ok("restart needed, run the program again")
                    time.sleep(0.5)
                    sys.exit()
                else:
                    sg.popup_error("wrong credentials!")
                    continue

            except DriveNotSetup as e:
                sg.popup_error(e)
                continue

    if event == "DELETE_CREDENTIALS":
        if sg.popup_ok_cancel("Are you sure you want to delete credentials!") == 'OK':
            config.delete_drive_credentials()
            window.close()
            window = main_window()

    if event == "SYNC_DRIVE":
        if sg.popup_ok_cancel("Sync to Drive?") == 'OK':
            cred_path = config.check_drive()
            main_folder_path = config.get_config("ROOT_DIRECTORY", "main_dir")
            if not main_folder_path:
                sg.popup_error("Folder Path not setup.")
                continue
            if not cred_path:
                sg.popup_error("credentials invalid!")
                continue
            else:
                zip_path = os.path.join(os.getcwd(), os.path.basename(main_folder_path))
                zip_created_path = create_zip(main_folder_path, zip_path)
                print(zip_created_path)
                if os.path.exists(zip_created_path):
                    id_ = upload_zip(zip_created_path, cred_path)
                    print(id_)
                    if id_:
                        config.update_config(id_, "GOOGLE_DRIVE_TOKEN", "drive_zip_id")
                        time: str = str(datetime.datetime.now().replace(microsecond=0, second=0))
                        config.update_config(time, "GOOGLE_DRIVE_TOKEN",
                                             "Last_Schedule")
                else:
                    raise Exception("zip not created")

    ###------- github setup
    if event == "SAVE_GITHUB":
        if not value["SETTINGS_ENV"]:
            sg.popup_error("Provide env variable for github token")
        else:
            env = value['SETTINGS_ENV']
            github_status = config.check_token_validity(env)
            if not github_status:
                sg.popup_error(f"Either token is expired or no token exists in variable {env}")
                continue
            config.save_github_token(env)
            sg.popup_auto_close("restart needed, run the program again")
            time.sleep(0.5)
            sys.exit()

    if event == "DELETE_GITHUB":
        if sg.popup_ok_cancel("Are you sure you want to delete github token?") == "OK":
            env = value['SETTINGS_ENV']
            config.update_config("", "GITHUB_TOKEN", "variable_name")
            config.update_config(True, "GITHUB_TOKEN", "enable")
            sg.popup_auto_close("restart needed!")
            time.sleep(0.5)
            sys.exit()

    ####------------------------ security check ------------------------####
    if not config.check_folder_malformed() and CHECK_SETTINGS_CREATED:
        sg.popup_error("Folder are deleted or changed, please create or change manually according to the config.")
        break

    #####------------------- create project section -------------------#####
    if event == "UPLOAD_EXISTING_PROJECT":
        if not CHECK_SETTINGS_CREATED:
            sg.popup_error("Folder settings not found. go to settings tab and create settings.")
            continue
        eu_window = existing_upload_window()
        while True:
            uep_event, uep_value = eu_window.read(timeout=400)
            print(uep_event, uep_value)
            if uep_event in ("Cancel_eu", sg.WINDOW_CLOSED):
                eu_window.close()
                break

            if uep_event == "UPLOAD-EXISTING-PROJECT":
                if uep_value['-EXISTING-PROJECT_TYPE-'] == "Project Type":
                    sg.popup_error("Select Project Type")
                    continue
                if not uep_value["-EXISTING-PROJECT_TYPE-"]:
                    sg.popup_error("select project type")
                    continue
                if not uep_value['EXISTING-PROJECT-PATH'] or not uep_value["-EXISTING-FOLDER_NAME-"]:
                    sg.popup_error("Value missing")
                    continue
                if not os.path.exists(uep_value['EXISTING-PROJECT-PATH']) or not os.path.isdir(uep_value['EXISTING-PROJECT-PATH']):
                    sg.popup_error("Folder doesn't exist")
                    continue

                project_type = next(i for i in ProjectType if i.value == uep_value['-EXISTING-PROJECT_TYPE-'])
                folder_name = uep_value["-EXISTING-FOLDER_NAME-"]
                root_path = config.get_config("SUB_DIRECTORY", project_type.value)
                existing_project_path = uep_value['EXISTING-PROJECT-PATH']
                try:
                    window.perform_long_operation(lambda: upload_existing_project(existing_project_path, folder_name, project_type, root_path),
                                                  end_key="UPLOAD_EXISTING_PROJECT_COMPLETED")

                except ProjectAlreadyCreated:
                    sg.popup_error("Project Already Created!")
                    continue
                break

    if event == "UPLOAD_EXISTING_PROJECT_COMPLETED":
        sg.popup_auto_close("Project Uploaded!")
        window.close()
        window = main_window()

    if event == "-TOGGLE-ENV-":
        ENV_PERMISSION = not ENV_PERMISSION
        window['-TOGGLE-ENV-'].update(image_data=toggle_btn_on if ENV_PERMISSION else toggle_btn_off)
    if event == "-TOGGLE-GITHUB-":
        GITHUB_PERMISSION = not GITHUB_PERMISSION
        window['-TOGGLE-GITHUB-'].update(image_data=toggle_btn_on if GITHUB_PERMISSION else toggle_btn_off)

    if event == '-CREATE-PROJECT-':
        if not CHECK_SETTINGS_CREATED:
            sg.popup_error("Folder settings not found. go to settings tab and create settings.")
        else:
            if not value["-FOLDER_NAME-"]:
                sg.popup_error("Values missing!")
                continue
            if value['-PROJECT_TYPE-'] == "Select Project Type":
                sg.popup_error("Select Project Type")
                continue
            if not GITHUB_PROFILE and GITHUB_PERMISSION:
                sg.popup_error("Github not set up!")
                continue
            if GITHUB_PERMISSION and not value["-REPO_NAME-"]:
                sg.popup_error("Enter Repo Name!")
                continue

            project_type = next(i for i in ProjectType if i.value == value['-PROJECT_TYPE-'])
            folder_name = value["-FOLDER_NAME-"]
            repo_name = value["-REPO_NAME-"]
            files = value["FILES_TO_CREATE"]
            if not files:
                files = []
            root_path = config.get_config("SUB_DIRECTORY", project_type.value)
            try:
                window.perform_long_operation(lambda: create_project(folder_name, ENV_PERMISSION, GITHUB_PERMISSION,
                                                                     repo_name, project_type, root_path, GITHUB_PROFILE, files),
                                              end_key="-CREATE_PROJECT_COMPLETED-")

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
        project_id = event.split("_")[-1]
        instance = get_project(project_id)
        instance.open_folder_in_pycharm()

    if "OPF_" in event:  # Open Folder
        project_id = event.split("_")[-1]
        instance = get_project(project_id)
        instance.open_project_folder()

    if "DP_" in event:  # Del Project
        if sg.popup_ok_cancel("Are you sure you want to delete project?") == "OK":
            project_id = event.split("_")[-1]
            instance = get_project(project_id)
            try:
                instance.delete_project(config.DB_NAME, GITHUB_PROFILE)
                window.close()
                window = main_window()
            except GitHubNotSetup:
                sg.popup_error("Either github token is expired or it does not exists, can perform github deletion.")
                continue

    if "OGL_" in event:  # Open Github Link
        project_id = event.split("_")[-1]
        instance = get_project(project_id)
        instance.open_github_link()

    if "DTD_" in event:
        project_id = event.split("_")[-1]
        instance = get_project(project_id)
        instance.dump_to_drive()

    if event == "EDIT_PROJECT_LAYOUT":
        epn_window = edit_project_window()
        while True:
            epn_event, epn_value = epn_window.read()
            if epn_event in ("Cancel", sg.WINDOW_CLOSED):
                epn_window.close()
                break
            names = [epn_value[i.value] for i in ProjectType]
            if epn_event == 'SAVE_EDIT_PROJECT_TYPE':
                if not any(names):
                    sg.popup_error("Values Missing")
                    continue
                if sg.popup_ok_cancel("Save Edits?") == "OK":
                    print(names)
                    # restart needed

window.close()
