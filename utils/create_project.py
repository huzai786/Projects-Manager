from config import config, ProjectType
from templates.projects import ProjectCreator

def create_project(folder_name, create_env, create_github, repo_name, template: ProjectType, root_path, github_user, files):
    for Type in ProjectType:
        if template == Type:
            project_path = create_instance(folder_name, create_env, create_github, repo_name, Type, root_path,
                             github_user, files)
            return project_path

def create_instance(folder_name, create_env, create_github, repo_name, project_type, root_path,
                     github_user, files):
    """Just saves the instance right away"""
    if create_env and not create_github:
        ins = ProjectCreator(folder_name, project_type, root_path, files)
        ins.create_env()

    elif not create_env and create_github:
        ins = ProjectCreator(folder_name, project_type, root_path, files)
        ins.create_github(repo_name, github_user)

    elif not create_env and not create_github:
        ins = ProjectCreator(folder_name, project_type, root_path, files)

    else:
        ins = ProjectCreator(folder_name, project_type, root_path, files)
        ins.create_github(repo_name, github_user)
        ins.create_env()
    ins.save_project(config.DB_NAME)

    return ins.project_path


