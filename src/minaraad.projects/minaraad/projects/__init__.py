from Products.CMFCore import utils as cmfutils
from Products.Archetypes import listTypes
from Products.Archetypes import atapi
from zope.i18nmessageid import MessageFactory

from minaraad.projects import config
MinaraadProjectMessageFactory = MessageFactory(u'minaraad.projects')

from Products.validation import validation
from validators import ProjectIdValidator, ProjectNumberValidator
validation.register(ProjectIdValidator('projectIdIsDate'))
validation.register(ProjectNumberValidator('projectNumber3Digits'))

from minaraad.projects import patches
patches.apply_all()

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    # imports packages and types for registration
    import content
    content  # pyflakes
    permissions = dict(
        Project='minaraad.projects: Add Project',
        Meeting='minaraad.projects: Add Meeting',
        DigiBib='minaraad.projects: Add DigiBib',
        AgendaItemProject='minaraad.projects: Add AgendaItemProject',
        Organisation='minaraad.projects: Add Organisation',
        ProjectContainer='minaraad.projects: Add ProjectContainer',
        MeetingContainer='minaraad.projects: Add MeetingContainer',
        OrganisationContainer='minaraad.projects: Add OrganisationContainer',
        )

    # Initialize portal content
    content_types, constructors, ftis = atapi.process_types(
        listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (config.PROJECTNAME, atype.archetype_name)
        cmfutils.ContentInit(
            kind,
            content_types=(atype, ),
            permission=permissions[atype.portal_type],
            extra_constructors=(constructor, ),
            ).initialize(context)
