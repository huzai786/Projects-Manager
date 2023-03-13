import os.path
import sys
import time
import webbrowser
from pathlib import Path

import PySimpleGUI as sg

from config import config, ProjectType
from utils.utils import upload_existing_project
from templates.utils import get_project
from utils.create_project import create_project


from Exceptions.exceptions import ProjectAlreadyCreated, DriveNotSetup, GitHubNotSetup, FolderNotExists, ZipNotCreated
from utils.windows import main_window, toggle_btn_on, toggle_btn_off, existing_upload_window, edit_project_window

sg.theme("LightBlue2")

ENV_PERMISSION = False
GITHUB_PERMISSION = False

CHECK_SETTINGS_CREATED = config.check_settings_created()
GITHUB_PROFILE = config.get_github_profile()
EDIT_PROJECT_NAMES = False
window = main_window()

while True:
    event, value = window.read()
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
            s = '\n'.join(config.get_config("PROJECT_TYPE_NAMES"))
            if sg.popup_ok_cancel(f"""Do you want the following folder type names, if not please change them from advance setting tab Once they are created, it can't be reversed. 
folder types: \n{s}""") != 'OK':
                sg.popup_error("Please configure project type names in the advance setting tab.")
                continue

            path, folder = value['SETTINGS_PATH'], value["SETTINGS_FOLD"]
            config.setup_config_path(path, folder)
            sg.popup_ok("restart needed, run the program again")
            time.sleep(0.5)
            sys.exit()

    if event == "PATH_DELETE":
        if sg.popup_ok_cancel(
                "Are you sure you want to delete all the projects!") == "OK":
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
            uep_event, uep_value = eu_window.read()
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
                    sg.popup_auto_close("It will take few seconds.")
                    window.perform_long_operation(lambda: upload_existing_project(existing_project_path, folder_name, project_type, root_path),
                                                  end_key="UPLOAD_EXISTING_PROJECT_COMPLETED")
                    break

                except ProjectAlreadyCreated:
                    sg.popup_error("Project Already Created!")
                    continue

        eu_window.close()



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
            files_folders = ["main.py"]
            if ENV_PERMISSION:
                files_folders.append("requirements.txt")

            root_path = config.get_config("SUB_DIRECTORY", project_type.value)
            try:
                window.perform_long_operation(lambda: create_project(folder_name, ENV_PERMISSION, GITHUB_PERMISSION,
                                                                     repo_name, project_type, root_path, GITHUB_PROFILE, files_folders),
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
                sg.popup_error("Either github token is expired or it does not exists, can't perform github deletion.")
                continue

    if "OGL_" in event:  # Open Github Link
        project_id = event.split("_")[-1]
        instance = get_project(project_id)
        instance.open_github_link()

    if "DTD_" in event:  # Dump to drive
        if sg.popup_ok_cancel("Dump to drive? this will delete github and uninstall env.") != "OK":
            continue

        project_id = event.split("_")[-1]
        instance = get_project(project_id)
        cred_path = config.get_config("GOOGLE_DRIVE_TOKEN", "credential_path")
        if not cred_path:
            sg.popup_error("Drive not setup")
            continue

        if not config.check_drive(cred_path):
            sg.popup_error("Credentials or Token Invalid!")
            continue

        try:
            window.perform_long_operation(lambda: instance.dump_to_drive(GITHUB_PROFILE, cred_path), end_key="DUMP_TO_DRIVE_COMPLETE")

        except GitHubNotSetup:
            sg.popup_error("Either github token is expired or it does not exists, can perform github deletion.")
            continue

        except FolderNotExists:
            sg.popup_error("Folders not created")
            continue

        except ZipNotCreated:
            sg.popup_error("Zip not created, try again.")
            continue

    if event == "DUMP_TO_DRIVE_COMPLETE":
        sg.popup_auto_close("uploaded to drive.")
        window.close()
        window = main_window()

    if event == "EDIT_PROJECT_TYPES":
        epn_window = edit_project_window()
        while True:
            epn_event, epn_value = epn_window.read()
            if epn_event in ("Cancel", sg.WINDOW_CLOSED):
                epn_window.close()
                break
            names = [epn_value[i.value].strip() for i in ProjectType]
            if epn_event == 'SAVE_EDIT_PROJECT_TYPE':
                if not any(names):
                    sg.popup_error("Values Missing")
                    continue

                if sg.popup_ok_cancel("Save Edits?") == "OK":
                    config.add_project_types(names)
                    sg.popup_auto_close("restart needed")
                    time.sleep(0.5)
                    sys.exit()

    if "DELFD_" in event:  # Delete from drive
        if sg.popup_ok_cancel("Delete from drive?") != "OK":
            continue
        project_id = event.split("_")[-1]
        instance = get_project(project_id)
        cred_path = config.get_config("GOOGLE_DRIVE_TOKEN", "credential_path")
        if not cred_path:
            sg.popup_error("Drive not setup")
            continue
        try:
            if instance.delete_zip_from_drive(cred_path):
                sg.popup_auto_close("Deletion successful")
                instance.delete_project(config.DB_NAME, GITHUB_PROFILE)
                window.close()
                window = main_window()

            else:
                sg.popup_auto_close("An Error occurred while deleting.")
                continue
        except ZipNotCreated:
            sg.popup_error("Zip not found!")
            continue
        except DriveNotSetup:
            sg.popup_error("drive not setup")
            continue


    if "DWFP_" in event:  # Download from drive
        if sg.popup_ok_cancel("Download project zip from drive?") != "OK":
            continue
        project_id = event.split("_")[-1]
        instance = get_project(project_id)
        webbrowser.open(instance.zip_info.url)

window.close()
