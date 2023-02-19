import os.path
import pickle
import random
import zipfile

from config import DB_NAME, ProjectType

import PySimpleGUI as sg


def check_folder_malformed(cfg):
    config = cfg.get_config()
    dirs = [config['ROOT_DIRECTORY']['main_dir']] + [v for k, v in config['SUB_DIRECTORY'].items() if k not in (
        "GOOGLE_DRIVE_TOKEN", "GITHUB_TOKEN")]
    for d in dirs:
        if not os.path.exists(d):
            return False
    return True

def create_zip(file_path, zip_name):
    if os.path.exists(file_path):
        _zip = zipfile.ZipFile(zip_name, 'w')
        _zip.write(file_path)
        _zip.close()
        return zip_name

def get_random_id():
    return "".join([str(random.randrange(0, 9)) for _ in range(8)])

def delete_records(db_name, project_id):
    with open(db_name, 'rb') as f:
        record = pickle.load(f)
        del record[project_id]
    with open(db_name, 'wb') as f:
        pickle.dump(record, f)

def save_records(db_name, instance, _id):
    if not os.path.exists(db_name):
        raise Exception("db doesn't exists")
    with open(db_name, 'rb') as f:
        record = pickle.load(f)
    record[_id] = instance
    with open(db_name, 'wb') as f:
        pickle.dump(record, f)

def get_records():
    with open(DB_NAME, 'rb') as f:
        data = pickle.load(f)
    return data

def generate_layout(instance):
    l = [
        [sg.Button("Open In Ide", key=f"OIP_{instance.id}")],
        [sg.Button("Open Folder", key=f"OPF_{instance.id}"), sg.Button("Del Project", key=f"DP_{instance.id}")],
    ]
    if instance.github_info:
        l.append([sg.Button("Open Github Link", key=f"OGL_{instance.id}")])

    ins_layout = sg.Frame(str(instance), l, key=instance.id, size=(250, 200), border_width=5, font="serif 11 bold")
    return ins_layout, instance.project_type


def get_layouts():
    records = get_records()
    layouts = {ProjectType.Professional_Projects: [],
              ProjectType.Fun_Personal: [],
              ProjectType.Coding_Problems: [],
              ProjectType.Learning: [],
              ProjectType.Progress: []}

    for ins_id, ins in records.items():
        layout, col_type = generate_layout(ins)
        for k, v in layouts.items():
            if k == col_type:
                layouts[col_type].append(layout)
    return layouts

def generate_project_showcase_layout():
    layouts = get_layouts()
    coding_problems_projects = [[f] for f in layouts.get(ProjectType.Coding_Problems)]
    fun_and_personal_projects = [[f] for f in layouts.get(ProjectType.Fun_Personal)]
    learning_projects_column = [[f] for f in layouts.get(ProjectType.Learning)]
    progress_projects = [[f] for f in layouts.get(ProjectType.Progress)]
    professional_projects = [[f] for f in layouts.get(ProjectType.Professional_Projects)]
    view_project_layout = [
        [
         sg.Frame("Coding Problems Projects", coding_problems_projects, size=(200, 1000), font=("sans sarif", 11,
                  "bold"), expand_y=True),
         sg.Frame("Fun/Personal Projects", fun_and_personal_projects, size=(200, 1000), font=("sans sarif", 11,
                  "bold"), expand_y=True),
         sg.Frame("Learning Projects", learning_projects_column, size=(200, 1000), font=("sans sarif", 11, "bold"),
                  expand_y=True),
         sg.Frame("Progress Projects", progress_projects, size=(200, 1000), font=("sans sarif", 11, "bold"),
                  expand_y=True),
         sg.Frame("Professional Work Projects", professional_projects, size=(200, 1000), font=("sans sarif", 11,
                                                                                               "bold"), expand_y=True)
        ]
    ]
    return view_project_layout


def __get_project(key):
    records = get_records()
    project_id = key.split("_")[1]
    project = records.get(project_id)
    return project