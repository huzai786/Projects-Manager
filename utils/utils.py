import PySimpleGUI as sg
from distutils.dir_util import copy_tree
from templates.utils import get_records
from utils.create_project import create_project
from config import config, ProjectType


def project_layout(instance):
    drive = config.check_drive(config.get_config("GOOGLE_DRIVE_TOKEN", "credential_path"))
    l = [
        [sg.VPush()],
        [sg.Button("Open In Ide", key=f"OIP_{instance.id}", size=(20, 1))],
        [sg.Button("Open Folder", key=f"OPF_{instance.id}", size=(20, 1))],
        [sg.Button("Del Project", key=f"DP_{instance.id}", size=(20, 1))]
    ]
    if drive:
        l.append([sg.Button("Dumped To Drive", key=f"DTD_{instance.id}", size=(20, 1))])
    if instance.github_info:
        l.append([sg.Button("Open Github Link", key=f"OGL_{instance.id}", size=(20, 1))])
    ins_layout = [sg.Frame(str(instance), l, key=instance.id, border_width=5, font="serif 11 bold")]
    return ins_layout, instance.project_type


def get_layouts() -> dict:
    records = get_records(config.DB_NAME)
    layouts = {i: [] for i in ProjectType}

    for ins_id, ins in records.items():
        if not ins.zip_info:
            layout, col_type = project_layout(ins)  # col_type: ProjectType
            for k, v in layouts.items():
                if k == col_type:
                    layouts[col_type].append(layout)
    return layouts


def generate_project_showcase_layout():
    layouts = get_layouts()
    view_project_layout = [[]]
    for l_type, layout in layouts.items():
        elem = sg.Frame(f"{l_type.value} Projects", layout, size=(200, 1000), font=("sans sarif", 11, "bold"), expand_y=True)
        view_project_layout[0].append(elem)
    return view_project_layout

def dumped_project_layout(record):
    drive = config.check_drive(config.get_config("GOOGLE_DRIVE_TOKEN", "credential_path"))
    l = [
        [sg.Text(str(record), font=("Sans Serif", 20, "bold"))],
        [sg.Text(f"Project Type: {record.project_type.value}")],
        [sg.Button("Download Project", key=f"DWFP_{record.id}")],
    ]
    if drive:
        l[2].append(sg.Button("Delete From drive", key=f"DELFD_{record.id}"))  # noqa

    ins_layout = [sg.Frame(str(record), l, border_width=5, font="serif 11 bold")]
    return ins_layout

def get_dumped_projects_Layout():
    records = get_records(config.DB_NAME)
    view_project_layout = [
        [sg.Text("Dumped Projects", font=("Sans serif", 25, "bold"))],
        [sg.HSep()]
    ]
    for ide, record in records.items():
        if record.zip_info:
            l = dumped_project_layout(record)
            view_project_layout.append(l)
    return view_project_layout


def upload_existing_project(existing_project_path, folder_name, project_type, root_path):
    project_path = create_project(folder_name, create_env=False, create_github=False, repo_name="",
                                  template=project_type, root_path=root_path, github_user=None, files=None)

    copy_tree(existing_project_path, project_path)


