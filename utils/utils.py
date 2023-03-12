import os
import shutil

import PySimpleGUI as sg
import shutil, errno
from templates.utils import get_records
from utils.create_project import create_project
from utils.project_type import ProjectType
from config import config


def generate_layout(instance):
    drive = config.check_drive()
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
    ins_layout = sg.Frame(str(instance), l, key=instance.id, border_width=5, font="serif 11 bold")
    return ins_layout, instance.project_type


def get_layouts():
    records = get_records()
    layouts = {ProjectType.Type1: [],
               ProjectType.Type2: [],
               ProjectType.Type3: [],
               ProjectType.Type4: [],
               ProjectType.Type5: []}

    for ins_id, ins in records.items():
        layout, col_type = generate_layout(ins)
        for k, v in layouts.items():
            if k == col_type:
                layouts[col_type].append(layout)
    return layouts


def generate_project_showcase_layout():
    layouts = get_layouts()
    type1_projects = [[f] for f in layouts.get(ProjectType.Type1)]
    type2_projects = [[f] for f in layouts.get(ProjectType.Type2)]
    type3_projects = [[f] for f in layouts.get(ProjectType.Type3)]
    type4_projects = [[f] for f in layouts.get(ProjectType.Type4)]
    type5_projects = [[f] for f in layouts.get(ProjectType.Type5)]
    view_project_layout = [
        [
            sg.Frame(f"{ProjectType.Type1.value} Projects", type1_projects, size=(200, 1000), font=("sans sarif", 11,
                                                                                                    "bold"),
                     expand_y=True),
            sg.Frame(f"{ProjectType.Type2.value} Projects", type2_projects, size=(200, 1000), font=("sans sarif", 11,
                                                                                                    "bold"),
                     expand_y=True),
            sg.Frame(f"{ProjectType.Type3.value} Projects", type3_projects, size=(200, 1000), font=("sans sarif", 11,
                                                                                                    "bold"),
                     expand_y=True),
            sg.Frame(f"{ProjectType.Type4.value} Projects", type4_projects, size=(200, 1000), font=("sans sarif", 11,
                                                                                                    "bold"),
                     expand_y=True),
            sg.Frame(f"{ProjectType.Type5.value} Projects", type5_projects, size=(200, 1000), font=("sans sarif", 11,
                                                                                                    "bold"),
                     expand_y=True)
        ]
    ]
    return view_project_layout


def get_project(project_id):
    records = get_records()
    project = records.get(project_id)
    return project


def create_zip(dir_path, zip_path):
    if os.path.exists(dir_path):
        zp = shutil.make_archive(zip_path, "zip", dir_path)

        return zp

def upload_existing_project(existing_project_path, folder_name, project_type, root_path):
    project_path = create_project(folder_name, create_env=False, create_github=False, repo_name="",
                                  template=project_type, root_path=root_path, github_user=None, files=None)

    copy(existing_project_path, project_path)

def copy(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc:
        if exc.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(src, dst)
        else:
            raise
