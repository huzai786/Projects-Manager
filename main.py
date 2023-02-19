import PySimpleGUI as sg

from utils.utils import check_folder_malformed, ProjectType, __get_project
from utils.frontend_utils import create_project

from Exceptions.exceptions import DriveNotSetup, GitHubNotSetup, ProjectAlreadyCreated
from windows import config_window, main_window, toggle_btn_on, toggle_btn_off
from config import config, DB_NAME

sg.theme("LightBlue2")

ENV_PERMISSION = False
GITHUB_PERMISSION = False

window = main_window()

while True:
    event, value = window.read(timeout=400)
    if event in (sg.WINDOW_CLOSED, "Cancel"):
        break

    if not config.get_config():
        choice, value = config_window()

        if choice in (sg.WINDOW_CLOSED, "Cancel"):
            break

        elif choice == "Continue" and value['PATH'] and value["FOLD"]:
            try:
                path, folder, token, env_variable = value['PATH'], value["FOLD"], value['TOKEN'], value['ENV']
                config.setup_config_path(path, folder, token, env_variable)
                window.close()
                window = main_window()

            except DriveNotSetup:
                sg.popup_error("Please Setup google drive credentials!")
                break

            except GitHubNotSetup:
                sg.popup_error("Either access token or env variable is incorrect!")
                break

        else:
            sg.popup_error("path or folder name missing")
            continue

    if not check_folder_malformed(config):
        sg.popup_error("Folder are deleted or changed, please create or change manually according to the config.")
        break

    if event == "-TOGGLE-ENV-":
        ENV_PERMISSION = not ENV_PERMISSION
        window['-TOGGLE-ENV-'].update(image_data=toggle_btn_on if ENV_PERMISSION else toggle_btn_off)
    if event == "-TOGGLE-GITHUB-":
        GITHUB_PERMISSION = not GITHUB_PERMISSION
        window['-TOGGLE-GITHUB-'].update(image_data=toggle_btn_on if GITHUB_PERMISSION else toggle_btn_off)

    if event == '-CREATE-PROJECT-':
        if not value["-FOLDER_NAME-"]:
            sg.popup_error("Values missing!")
            continue
        if value['-TEMPLATE-'] == "Select Template":
            sg.popup_error("Select Template")
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
                    repo_name, template, root_path), end_key="-CREATE_PROJECT_COMPLETED-")

        except ProjectAlreadyCreated:
            sg.popup_error("Project Already Created!")
            continue

        sg.popup_auto_close("this will take a moment to create please wait!")
        window["-CREATE-PROJECT-"].update(disabled=True)

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
            instance.delete_project(DB_NAME)
            window.close()
            window = main_window()

    if "OGL_" in event:  # Open Github Link
        instance = __get_project(event)
        instance.open_github_link()

window.close()
