from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi

from minaraad.projects import config
from minaraad.projects.interfaces import IProjectContainer

container_schema = atapi.BaseFolderSchema.copy()


class ProjectContainer(atapi.BaseFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (atapi.BaseFolder.__implements__, )
    implements(IProjectContainer)

    _at_rename_after_creation = True
    schema = container_schema

    def list_projects(self):
        return self.contentValues()

    def exclude_from_nav(self):
        """Always exclude this folder from navigation.
        """
        return True

atapi.registerType(ProjectContainer, config.PROJECTNAME)
