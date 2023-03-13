from pathlib import Path

import PySimpleGUI as sg

from utils.utils import generate_project_showcase_layout, get_dumped_projects_Layout
from config import config, ProjectType

toggle_btn_off = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAED0lEQVRYCe1WTWwbRRR+M/vnv9hO7BjHpElMKSlpqBp6gRNHxAFVcKM3qgohQSqoqhQ45YAILUUVDRxAor2VAweohMSBG5ciodJUSVqa/iikaePEP4nj2Ovdnd1l3qqJksZGXscVPaylt7Oe/d6bb9/svO8BeD8vA14GvAx4GXiiM0DqsXv3xBcJU5IO+RXpLQvs5yzTijBmhurh3cyLorBGBVokQG9qVe0HgwiXLowdy9aKsY3g8PA5xYiQEUrsk93JTtjd1x3siIZBkSWQudUK4nZO1w3QuOWXV+HuP/fL85klAJuMCUX7zPj4MW1zvC0Ej4yMp/w++K2rM9b70sHBYCjo34x9bPelsgp/XJksZ7KFuwZjr3732YcL64ttEDw6cq5bVuCvgy/sje7rT0sI8PtkSHSEIRIKgCQKOAUGM6G4VoGlwiqoVd2Za9Vl8u87bGJqpqBqZOj86eEHGNch+M7otwHJNq4NDexJD+59RiCEQG8qzslFgN8ibpvZNsBifgXmFvJg459tiOYmOElzYvr2bbmkD509e1ylGEZk1Y+Ssfan18n1p7vgqVh9cuiDxJPxKPT3dfGXcN4Tp3dsg/27hUQs0qMGpRMYjLz38dcxS7Dm3nztlUAb38p0d4JnLozPGrbFfBFm79c8hA3H2AxcXSvDz7/+XtZE1kMN23hjV7LTRnKBh9/cZnAj94mOCOD32gi2EUw4FIRUMm6LGhyiik86nO5NBdGRpxYH14bbjYfJteN/OKR7UiFZVg5T27QHYu0RBxoONV9W8KQ7QVp0iXdE8fANUGZa0QAvfhhXlkQcmjJZbt631oIBnwKmacYoEJvwiuFgWncWnXAtuVBBEAoVVXWCaQZzxmYuut68b631KmoVBEHMUUrJjQLXRAQVSxUcmrKVHfjWWjC3XOT1FW5QrWpc5IJdQhDKVzOigEqS5dKHMVplnNOqrmsXqUSkn+YzWaHE9RW1FeXL7SKZXBFUrXW6jIV6YTEvMAUu0W/G3kcxPXP5ylQZs4fa6marcWvvZfJu36kuHjlc/nMSuXz+/ejxgqPFpuQ/xVude9eu39Jxu27OLvBGoMjrUN04zrNMbgVmOBZ96iPdPZmYntH5Ls76KuxL9NyoLA/brav7n382emDfHqeooXyhQmARVhSnAwNNMx5bu3V1+habun5nWdXhwJZ2C5mirTesyUR738sv7g88UQ0rEkTDlp+1wwe8Pf0klegUenYlgyg7bby75jUTITs2rhCAXXQ2vwxz84vlB0tZ0wL4NEcLX/04OrrltG1s8aOrHhk51SaK0us+n/K2xexBxljcsm1n6x/Fuv1PCWGiKOaoQCY1Vb9gWPov50+fdEqd21ge3suAlwEvA14G/ucM/AuppqNllLGPKwAAAABJRU5ErkJggg=='
toggle_btn_on = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAD+UlEQVRYCe1XzW8bVRCffbvrtbP+2NhOD7GzLm1VoZaPhvwDnKBUKlVyqAQ3/gAkDlWgPeVQEUCtEOIP4AaHSI0CqBWCQyXOdQuRaEFOk3g3IMWO46+tvZ+PeZs6apq4ipON1MNafrvreTPzfvub92bGAOEnZCBkIGQgZOClZoDrh25y5pdjruleEiX+A+rCaQo05bpuvJ/+IHJCSJtwpAHA/e269g8W5RbuzF6o7OVjF8D3Pr4tSSkyjcqfptPDMDKSleW4DKIggIAD5Yf+Oo4DNg6jbUBlvWLUNutAwZu1GnDjzrcXzGcX2AHw/emFUV6Sfk0pqcKpEydkKSo9q3tkz91uF5aWlo1Gs/mYc+i7tz4//19vsW2AU9O381TiioVCQcnlRsWeQhD3bJyH1/MiFLICyBHiuzQsD1arDvypW7DR9nzZmq47q2W95prm+I9fXfqXCX2AF2d+GhI98Y8xVX0lnxvl2UQQg0csb78ag3NjEeD8lXZ7pRTgftmCu4864OGzrq+5ZU0rCa3m+NzXlzvoAoB3+M+SyWQuaHBTEzKMq/3BMbgM+FuFCDBd9kK5XI5PJBKqLSev+POTV29lKB8rT0yMD0WjUSYLZLxzNgZvIHODOHuATP72Vwc6nQ4Uiw8MUeBU4nHS5HA6TYMEl02wPRcZBJuv+ya+UCZOIBaLwfCwQi1Mc4QXhA+PjWRkXyOgC1uIhW5Qd8yG2TK7kSweLcRGKKVnMNExWWBDTQsH9qVmtmzjiThQDs4Qz/OUSGTwcLwIQTLW58i+yOjpXDLqn1tgmDzXzRCk9eDenjo9yhvBmlizrB3V5dDrNTuY0A7opdndStqmaQLPC1WCGfShYRgHdLe32UrV3ntiH9LliuNrsToNlD4kruN8v75eafnSgC6Luo2+B3fGKskilj5muV6pNhk2Qqg5v7lZ51nBZhNBjGrbxfI1+La5t2JCzfD8RF1HTBGJXyDzs1MblONulEqPDVYXgwDIfNx91IUVbAbY837GMur+/k/XZ75UWmJ77ou5mfM1/0x7vP1ls9XQdF2z9uNsPzosXPNFA5m0/EX72TBSiqsWzN8z/GZB08pWq9VeEZ+0bjKb7RTD2i1P4u6r+bwypo5tZUumEcDAmuC3W8ezIqSGfE6g/sTd1W5p5bKjaWubrmWd29Fu9TD0GlYlmTx+8tTJoZeqYe2BZC1/JEU+wQR5TVEUPptJy3Fs+Vkzgf8lemqHumP1AnYoMZSwsVEz6o26i/G9Lgitb+ZmLu/YZtshfn5FZDPBCcJFQRQ+8ih9DctOFvdLIKHH6uUQnq9yhFu0bec7znZ+xpAGmuqef5/wd8hAyEDIQMjAETHwP7nQl2WnYk4yAAAAAElFTkSuQmCC'


project_type_options = [i.value for i in ProjectType]

def main_window():
    #### ------------   Create Project Layout   ------------- ####

    cps_options = [
        [sg.Text("Folder Name:"), sg.Input(key='-FOLDER_NAME-')],
        [sg.Text("Create virtualenv:"), sg.Button(image_data=toggle_btn_off, key='-TOGGLE-ENV-', button_color=(
            sg.theme_background_color(), sg.theme_background_color()), border_width=0)],
        [sg.Text("Create Github:   "), sg.Button(image_data=toggle_btn_off, key='-TOGGLE-GITHUB-', button_color=(
            sg.theme_background_color(), sg.theme_background_color()), border_width=0)],
        [sg.T("Repo Name: "), sg.Input(key='-REPO_NAME-')],
        [sg.OptionMenu(project_type_options, default_value='Select Project Type', key='-PROJECT_TYPE-', size=(30, 2))],
        [sg.VPush()],
        [sg.Button("Create New Project", key="-CREATE-PROJECT-", size=(30, 2), button_color="black")]

    ]
    cps_layout = [
        [sg.Frame('create new project', cps_options, size=(250, 400), font=("sans sarif", 18, "bold"),
                  title_color="black")]
    ]
    create_project_form = sg.Column(cps_layout)

    # view project section
    view_project_layout = generate_project_showcase_layout()
    view_project_section = sg.Column(view_project_layout, scrollable=True, size=(1100, 500),
                                     vertical_scroll_only=True)

    #### ------------   Manager Project Layout   ------------- ####
    project_manager_tab = [
        [sg.Button("Upload Existing Project", key="UPLOAD_EXISTING_PROJECT", size=(20, 1), button_color="black"),
         sg.Text("Projects Manager", justification="center", font=("Times New Roman", 25, "bold"), size=300, text_color="black")],
        [sg.HSep(pad=((30, 30), (0, 10)), color="black")],
        [create_project_form, view_project_section],
        [sg.P(), sg.Cancel("Close", key="Cancel", size=(14, 1))]
    ]

    #### ------------     Setting Tab Layout     ------------- ####
    ### ---------- setup Project path
    project_path = config.get_config("ROOT_DIRECTORY", "main_dir")
    l11 = [
        [sg.Text("Enter project path:\t"), sg.InputText(key='SETTINGS_PATH', disabled=True)],
        [sg.Text('Enter folder name: \t'), sg.InputText(key='SETTINGS_FOLD', disabled=True)],
    ] if project_path else [
        [sg.Text("Enter project path:\t"), sg.InputText(key='SETTINGS_PATH')],
        [sg.Text('Enter folder name: \t'), sg.InputText(key='SETTINGS_FOLD')],
    ]
    l12 = [
        [sg.Text("project path: ", font=("Times New Roman", 15)), sg.Text(project_path if project_path else "Not Set",
                                                                          font=("Times New Roman", 15))],
    ]
    projectPathLayout = [
        [sg.Column(l11), sg.Push(), sg.Column(l12)],
        [sg.B("Setup path", key="PATH_SETUP", disabled=True) if project_path else sg.B("Setup path", key="PATH_SETUP"),
         sg.B("Delete Folder", key="PATH_DELETE") if project_path else sg.B("Delete Folder", key="PATH_DELETE",
                                                                            disabled=True)]
    ]

    ### ---------- setup github settings
    gthb = config.get_github_profile()
    github_var = config.get_config("GITHUB_TOKEN", "variable_name")
    l21 = [
        [sg.T("save github personal access token and enter the environment variable name.\n")],
        [sg.T("Enter environment variable name:"), sg.InputText(key="SETTINGS_ENV", disabled=True) if gthb else
        sg.InputText(key="SETTINGS_ENV")],
    ]
    l22 = [
        [sg.Text("Github Token: ", font=("Times New Roman", 15)),
         sg.Text(github_var if github_var else "Not Set", font=("Times New Roman", 15))],
    ]
    github_setup_layout = [
        [sg.Column(l21), sg.Push(), sg.Column(l22)],
        [sg.B("Save", key="SAVE_GITHUB", disabled=True) if gthb else sg.B("Save", key="SAVE_GITHUB"),
         sg.B("Delete", key="DELETE_GITHUB") if gthb else
         sg.B("Delete", key="DELETE_GITHUB", disabled=True)]
    ]

    ### ---------- setup drive settings
    drive = config.check_drive(config.get_config("GOOGLE_DRIVE_TOKEN", "credential_path"))
    l31 = [
        [sg.Text("If drive is not setup, click the setup button to open google for authorization.")]
    ]
    if drive:
        l31.extend([[sg.Button("Delete Credentials", key="DELETE_CREDENTIALS")]])
    else:
        l31.extend(
            [
                [sg.Text("Browse file: "), sg.InputText(key="CREDENTIALS_FILE"),
                 sg.FileBrowse(initial_folder=Path.home(), file_types=[("Json files", "*.json")])],
                [sg.Button("Setup Drive", key="DRIVE_SETUP")]
            ]
        )

    l32 = [
        [sg.Text("Drive credentials: ", font=("Times New Roman", 15)),
         sg.Text(Path(drive).name if drive else "Not Set", font=("Times New Roman", 15))]
    ]
    drive_setup_layout = [
        [sg.Column(l31), sg.Push(), sg.Column(l32)],
    ]

    settings_tab = [
        [sg.Frame("Project Path", projectPathLayout, font=("Times New Roman", 25, "bold"), pad=10, size=(1300, 140))],
        [sg.Frame("Github setup", github_setup_layout, font=("Times New Roman", 25, "bold"), pad=10, size=(1300, 180))],
        [sg.Frame("Drive Setup", drive_setup_layout, font=("Times New Roman", 25, "bold"), pad=10, size=(1300, 190))]
    ]

    #### ------------     Dumped Projects Layout     ------------- ####
    completed_and_dumped_projects = get_dumped_projects_Layout()
    #### ------------     Advance Settings Layout     ------------- ####
    advance_settings = [[sg.HSep()]]
    for i, v in enumerate(project_type_options):
        advance_settings.append([sg.Text(f"Type{i + 1}: ", font=("Times New Roman", 15), border_width=6),
                         sg.Text(v, font=("Times New Roman", 15), border_width=6)])
        advance_settings.append([sg.HSep()])

    ad_layout = [
        [sg.Text("Project Types", justification="c", font=("Times New Roman", 25, "bold"))],
        [sg.Column(advance_settings)],
        [sg.Button("Edit Project Names", key="EDIT_PROJECT_TYPES", disabled=True) if config.get_config("ROOT_DIRECTORY", "main_dir")
         else sg.Button("Edit Project Names", key="EDIT_PROJECT_TYPES")]
    ]
    tab_group = [
        [
            sg.TabGroup(
                [[
                    sg.Tab("Manage Projects", project_manager_tab),
                    sg.Tab("Dumped Projects", completed_and_dumped_projects),
                    sg.Tab("Settings", settings_tab),
                    sg.Tab("Advance Settings", ad_layout),
                ]],
                tab_location='topleft',
                title_color="Black",
                tab_background_color="white",
                selected_title_color="white",
                selected_background_color="black"
            )
        ]
    ]

    window = sg.Window("Projects Manager", tab_group, size=(1380, 650))
    return window


def existing_upload_window():
    layout = [
        [sg.Text("UPLOAD EXISTING PROJECT", font=("Times New Roman", 20, "bold"))],
        [sg.Text("Folder Name:"), sg.Input(key='-EXISTING-FOLDER_NAME-')],
        [sg.Text("Select Project Type: "), sg.OptionMenu(project_type_options, default_value='Project Type', key='-EXISTING-PROJECT_TYPE-', size=(30, 2))],
        [sg.Text("Select Folder: "), sg.InputText("", key="EXISTING-PROJECT-PATH"), sg.FolderBrowse()],
        [sg.VPush()],
        [sg.Button("Upload", key="UPLOAD-EXISTING-PROJECT", size=(14, 1)), sg.Cancel("Close", key="Cancel_eu", size=(14, 1))]
    ]
    window = sg.Window("Projects Manager", layout, size=(1380 // 2, 650 // 2))
    return window

def edit_project_window():
    edit_projects_name_layout = [[sg.Text("Edit Project Type Names", font=("Times New Roman", 20, "bold"))]]
    for i, v in enumerate(project_type_options):
        edit_projects_name_layout.append([sg.Text(f"Type{i + 1}: ", font=("Times New Roman", 15), border_width=4),
                                sg.InputText(v, key=v, font=("Times New Roman", 15))])
    edit_projects_name_layout.append([sg.Button("Save", key="SAVE_EDIT_PROJECT_TYPE", size=(14, 1)),
                                      sg.Cancel("Close", key="Cancel", size=(14, 1))])
    window = sg.Window("Projects Manager", edit_projects_name_layout, size=(1380 // 2, 650 // 2))

    return window
