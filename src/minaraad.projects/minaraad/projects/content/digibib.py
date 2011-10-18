from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi

from minaraad.projects import config
from minaraad.projects.interfaces import IDigiBib

digibib_schema = atapi.BaseFolderSchema.copy() + atapi.Schema()


class DigiBib(atapi.BaseFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (atapi.BaseFolder.__implements__, )
    implements(IDigiBib)

    _at_rename_after_creation = True
    schema = digibib_schema

    def list_projects(self):
        return self.projects.list_projects()

    def list_meetings(self):
        return self.meetings.list_meetings()


atapi.registerType(DigiBib, config.PROJECTNAME)
