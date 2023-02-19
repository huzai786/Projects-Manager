from templates.base import Base
from config import config

class CodingProblem(Base):
    root_path = config.get_config("SUB_DIRECTORY", "coding_problems")
    files_to_create = []

    def __init__(self, project_name, project_type, root_path):
        super().__init__(project_name, project_type, root_path)

class FunPersonal(Base):
    root_path = config.get_config("SUB_DIRECTORY", "fun_personal")

    def __init__(self, project_name, project_type, root_path):
        super().__init__(project_name, project_type, root_path)

class Learning(Base):
    root_path = config.get_config("SUB_DIRECTORY", "learning")

    def __init__(self, project_name, project_type, root_path):
        super().__init__(project_name, project_type, root_path)

class Progress(Base):
    root_path = config.get_config("SUB_DIRECTORY", "progress")

    def __init__(self, project_name, project_type, root_path):
        super().__init__(project_name, project_type, root_path)

class Professional_Project(Base):
    root_path = config.get_config("SUB_DIRECTORY", "project")

    def __init__(self, project_name, project_type, root_path):
        super().__init__(project_name, project_type, root_path)

