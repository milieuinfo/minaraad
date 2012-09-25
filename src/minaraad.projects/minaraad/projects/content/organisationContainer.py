from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi

from minaraad.projects import config
from minaraad.projects.interfaces import IOrganisationContainer

container_schema = atapi.BaseFolderSchema.copy()


class OrganisationContainer(atapi.BaseFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(IOrganisationContainer)

    _at_rename_after_creation = True
    schema = container_schema

    def list_organisations(self):
        return self.contentValues()


atapi.registerType(OrganisationContainer, config.PROJECTNAME)
