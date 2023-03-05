from utils.projectType import ProjectType
from templates.project_templates import CodingProblem, Professional_Project, Progress, FunPersonal, Learning

from config import DB_NAME

def create_project(folder_name, create_env, create_github, repo_name, template: ProjectType, root_path, github_user):
    if template == ProjectType.Professional_Projects:
        _create_instance(Professional_Project, folder_name, create_env, create_github, repo_name,
                         ProjectType.Professional_Projects, root_path, github_user)

    if template == ProjectType.Progress:
        _create_instance(Progress, folder_name, create_env, create_github, repo_name, ProjectType.Progress, root_path, github_user)

    if template == ProjectType.Learning:
        _create_instance(Learning, folder_name, create_env, create_github, repo_name, ProjectType.Learning, root_path, github_user)

    if template == ProjectType.Coding_Problems:
        _create_instance(CodingProblem, folder_name, create_env, create_github, repo_name,
                         ProjectType.Coding_Problems, root_path, github_user)

    if template == ProjectType.Fun_Personal:
        _create_instance(FunPersonal, folder_name, create_env, create_github, repo_name, ProjectType.Fun_Personal, root_path, github_user)


def _create_instance(Class, folder_name, create_env, create_github, repo_name, project_type, root_path, github_user):
    """Just saves the instance right away"""
    if create_env and not create_github:
        ins = Class(folder_name, project_type, root_path)
        ins.create_env()

    elif not create_env and create_github:
        ins = Class(folder_name, project_type, root_path)
        ins.create_github(repo_name, github_user)

    elif not create_env and not create_github:
        ins = Class(folder_name, project_type, root_path)

    else:
        ins = Class(folder_name, project_type, root_path)
        ins.create_github(repo_name, github_user)
        ins.create_env()
    ins.save_project(DB_NAME)


