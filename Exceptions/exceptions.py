from github.GithubException import UnknownObjectException

class DriveNotSetup(Exception):
    pass

class ProjectAlreadyCreated(Exception):
    pass

class GithubNotCreated(Exception):
    pass

class RepoNotExists(UnknownObjectException):
    pass

class GitHubNotSetup(Exception):
    pass


class FolderNotExists(AttributeError):
    pass
