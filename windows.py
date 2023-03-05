
import PySimpleGUI as sg

from utils.utils import generate_project_showcase_layout, checkDrive
from utils.projectType import ProjectType
from config import config

toggle_btn_off = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAED0lEQVRYCe1WTWwbRRR+M/vnv9hO7BjHpElMKSlpqBp6gRNHxAFVcKM3qgohQSqoqhQ45YAILUUVDRxAor2VAweohMSBG5ciodJUSVqa/iikaePEP4nj2Ovdnd1l3qqJksZGXscVPaylt7Oe/d6bb9/svO8BeD8vA14GvAx4GXiiM0DqsXv3xBcJU5IO+RXpLQvs5yzTijBmhurh3cyLorBGBVokQG9qVe0HgwiXLowdy9aKsY3g8PA5xYiQEUrsk93JTtjd1x3siIZBkSWQudUK4nZO1w3QuOWXV+HuP/fL85klAJuMCUX7zPj4MW1zvC0Ej4yMp/w++K2rM9b70sHBYCjo34x9bPelsgp/XJksZ7KFuwZjr3732YcL64ttEDw6cq5bVuCvgy/sje7rT0sI8PtkSHSEIRIKgCQKOAUGM6G4VoGlwiqoVd2Za9Vl8u87bGJqpqBqZOj86eEHGNch+M7otwHJNq4NDexJD+59RiCEQG8qzslFgN8ibpvZNsBifgXmFvJg459tiOYmOElzYvr2bbmkD509e1ylGEZk1Y+Ssfan18n1p7vgqVh9cuiDxJPxKPT3dfGXcN4Tp3dsg/27hUQs0qMGpRMYjLz38dcxS7Dm3nztlUAb38p0d4JnLozPGrbFfBFm79c8hA3H2AxcXSvDz7/+XtZE1kMN23hjV7LTRnKBh9/cZnAj94mOCOD32gi2EUw4FIRUMm6LGhyiik86nO5NBdGRpxYH14bbjYfJteN/OKR7UiFZVg5T27QHYu0RBxoONV9W8KQ7QVp0iXdE8fANUGZa0QAvfhhXlkQcmjJZbt631oIBnwKmacYoEJvwiuFgWncWnXAtuVBBEAoVVXWCaQZzxmYuut68b631KmoVBEHMUUrJjQLXRAQVSxUcmrKVHfjWWjC3XOT1FW5QrWpc5IJdQhDKVzOigEqS5dKHMVplnNOqrmsXqUSkn+YzWaHE9RW1FeXL7SKZXBFUrXW6jIV6YTEvMAUu0W/G3kcxPXP5ylQZs4fa6marcWvvZfJu36kuHjlc/nMSuXz+/ejxgqPFpuQ/xVude9eu39Jxu27OLvBGoMjrUN04zrNMbgVmOBZ96iPdPZmYntH5Ls76KuxL9NyoLA/brav7n382emDfHqeooXyhQmARVhSnAwNNMx5bu3V1+habun5nWdXhwJZ2C5mirTesyUR738sv7g88UQ0rEkTDlp+1wwe8Pf0klegUenYlgyg7bby75jUTITs2rhCAXXQ2vwxz84vlB0tZ0wL4NEcLX/04OrrltG1s8aOrHhk51SaK0us+n/K2xexBxljcsm1n6x/Fuv1PCWGiKOaoQCY1Vb9gWPov50+fdEqd21ge3suAlwEvA14G/ucM/AuppqNllLGPKwAAAABJRU5ErkJggg=='
toggle_btn_on = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAD+UlEQVRYCe1XzW8bVRCffbvrtbP+2NhOD7GzLm1VoZaPhvwDnKBUKlVyqAQ3/gAkDlWgPeVQEUCtEOIP4AaHSI0CqBWCQyXOdQuRaEFOk3g3IMWO46+tvZ+PeZs6apq4ipON1MNafrvreTPzfvub92bGAOEnZCBkIGQgZOClZoDrh25y5pdjruleEiX+A+rCaQo05bpuvJ/+IHJCSJtwpAHA/e269g8W5RbuzF6o7OVjF8D3Pr4tSSkyjcqfptPDMDKSleW4DKIggIAD5Yf+Oo4DNg6jbUBlvWLUNutAwZu1GnDjzrcXzGcX2AHw/emFUV6Sfk0pqcKpEydkKSo9q3tkz91uF5aWlo1Gs/mYc+i7tz4//19vsW2AU9O381TiioVCQcnlRsWeQhD3bJyH1/MiFLICyBHiuzQsD1arDvypW7DR9nzZmq47q2W95prm+I9fXfqXCX2AF2d+GhI98Y8xVX0lnxvl2UQQg0csb78ag3NjEeD8lXZ7pRTgftmCu4864OGzrq+5ZU0rCa3m+NzXlzvoAoB3+M+SyWQuaHBTEzKMq/3BMbgM+FuFCDBd9kK5XI5PJBKqLSev+POTV29lKB8rT0yMD0WjUSYLZLxzNgZvIHODOHuATP72Vwc6nQ4Uiw8MUeBU4nHS5HA6TYMEl02wPRcZBJuv+ya+UCZOIBaLwfCwQi1Mc4QXhA+PjWRkXyOgC1uIhW5Qd8yG2TK7kSweLcRGKKVnMNExWWBDTQsH9qVmtmzjiThQDs4Qz/OUSGTwcLwIQTLW58i+yOjpXDLqn1tgmDzXzRCk9eDenjo9yhvBmlizrB3V5dDrNTuY0A7opdndStqmaQLPC1WCGfShYRgHdLe32UrV3ntiH9LliuNrsToNlD4kruN8v75eafnSgC6Luo2+B3fGKskilj5muV6pNhk2Qqg5v7lZ51nBZhNBjGrbxfI1+La5t2JCzfD8RF1HTBGJXyDzs1MblONulEqPDVYXgwDIfNx91IUVbAbY837GMur+/k/XZ75UWmJ77ou5mfM1/0x7vP1ls9XQdF2z9uNsPzosXPNFA5m0/EX72TBSiqsWzN8z/GZB08pWq9VeEZ+0bjKb7RTD2i1P4u6r+bwypo5tZUumEcDAmuC3W8ezIqSGfE6g/sTd1W5p5bKjaWubrmWd29Fu9TD0GlYlmTx+8tTJoZeqYe2BZC1/JEU+wQR5TVEUPptJy3Fs+Vkzgf8lemqHumP1AnYoMZSwsVEz6o26i/G9Lgitb+ZmLu/YZtshfn5FZDPBCcJFQRQ+8ih9DctOFvdLIKHH6uUQnq9yhFu0bec7znZ+xpAGmuqef5/wd8hAyEDIQMjAETHwP7nQl2WnYk4yAAAAAElFTkSuQmCC'
button_create_path = b"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"
def main_window():
    template_options = [i.value for i in ProjectType]
    cps_options = [
        [sg.Text("Folder Name:"), sg.Input(key='-FOLDER_NAME-')],
        [sg.Text("Create virtualenv:"), sg.Button(image_data=toggle_btn_off, key='-TOGGLE-ENV-', button_color=(
            sg.theme_background_color(), sg.theme_background_color()), border_width=0)],
        [sg.Text("Create Github:   "), sg.Button(image_data=toggle_btn_off, key='-TOGGLE-GITHUB-', button_color=(
            sg.theme_background_color(), sg.theme_background_color()), border_width=0)],
        [sg.T("Repo Name: "), sg.Input(key='-REPO_NAME-')],
        [sg.OptionMenu(template_options, default_value='Select Template', key='-TEMPLATE-')],
        [sg.Button("Create", key="-CREATE-PROJECT-", size=(15, 2), button_color="black")]
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
        [sg.Text("Projects Manager", justification="center", font=("Times New Roman", 25, "bold"), size=300,
                 text_color="black")],
        [sg.HSep(pad=((30, 30), (0, 10)), color="black")],
        [create_project_form, view_project_section],
        [sg.P(), sg.Cancel("Close", key="Cancel")]
    ]

                #### ------------     Setting Tab Layout     ------------- ####
    project_path = config.get_config("ROOT_DIRECTORY", "main_dir")
    l11 = [
        [sg.Text("Enter project path:\t"), sg.InputText(key='SETTINGS_PATH')],
        [sg.Text('Enter folder name: \t'), sg.InputText(key='SETTINGS_FOLD')],
    ]
    l12 = [
        [sg.Text("project path: ", font=("Times New Roman", 20, "bold")), sg.Text(project_path if project_path else "Not Set",
                                                                                  font=("Times New Roman", 20, "bold"))],
    ]
    l21 = [
        [sg.T("save github personal access token and enter the environment variable name.\n")],
        [sg.T("Enter environment variable name:\t"), sg.InputText(key="SETTINGS_ENV")],

    ]
    l22 = [
        [sg.Text("Github Token: ", font=("Times New Roman", 20, "bold")),
         sg.Text(config.get_config("GITHUB_TOKEN", "variable_name") if config.get_config("GITHUB_TOKEN", "variable_name") else "Not Set",
                 font=("Times New Roman", 20, "bold"))],
    ]
    drive = checkDrive()
    l31 = [
        [sg.Text("If drive is not setup, click the setup button to open google for authorization.")]
    ]
    if not drive:
        l31.append([sg.Button("Setup Drive", key="DRIVE_SETUP")])
    l32 = [
        [sg.Text("Drive Status: ", font=("Times New Roman", 20, "bold")),
         sg.Text("Setup" if drive else "Not Set",
                 font=("Times New Roman", 20, "bold"))]
    ]

    projectPathLayout = [
        [sg.Column(l11), sg.Push(), sg.Column(l12)],
        [sg.B("Setup path", key="PATH_SETUP")]
    ]
    github_setup_layout = [
        [sg.Column(l21), sg.Push(), sg.Column(l22)],
        [sg.B("Save", key="SAVE_GITHUB")]
    ]
    drive_setup_layout = [
        [sg.Column(l31), sg.Push(), sg.Column(l32)],
    ]
    settings_tab = [
        [sg.Frame("Project Path", projectPathLayout, font=("Times New Roman", 25, "bold"), pad=10, size=(1300, 140))],
        [sg.Frame("Github setup", github_setup_layout, font=("Times New Roman", 25, "bold"), pad=10, size=(1300, 180))],
        [sg.Frame("Drive Setup", drive_setup_layout, font=("Times New Roman", 25, "bold"), pad=10, size=(1300, 150))]
    ]

                #### ------------     Dumped Projects Layout     ------------- ####
    completed_and_dumped_projects = [
        [sg.Text("asodjsdo")],
        [sg.Text("asodjsdo")],
        [sg.Text("asodjsdo")]
    ]

    tab_group = [
        [
            sg.TabGroup(
                [[
                    sg.Tab("Manage Projects", project_manager_tab),
                    sg.Tab("Settings", settings_tab),
                    sg.Tab("Dumped Projects", completed_and_dumped_projects),
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
