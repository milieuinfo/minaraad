from zope.app.component.hooks import getSite
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import \
     ReferenceBrowserWidget
from Products.CMFCore.utils import getToolByName

from minaraad.projects import config
from minaraad.projects import MinaraadProjectMessageFactory as _
from minaraad.projects.interfaces import IAgendaItemProject

from base_agendaitem import BaseAgendaItem, base_agendaitem_schema

agendaitem_schema = base_agendaitem_schema + atapi.Schema((
    atapi.TextField(
        name='summary',
        allowable_content_types=('text/html', ),
        default_content_type='text/html',
        default_output_type='text/html',
        widget = atapi.RichWidget(
            label = _(u'label_description',
                      default=u'Description')
            )
        ),

    atapi.ReferenceField(
        name='project',
        relationship='discussedProject',
        multiValued=0,
        languageIndependent = 1,
        allowed_types=('Project', ),
        widget=ReferenceBrowserWidget(
            # Note that we have changed referencebrowser.js to use the
            # referencebrowser_popup_simple.pt when the field name is
            # 'project'.
            label=_('label_project',
                    default='Project'),
            only_for_review_states=('active', ),
            show_review_state=0,
            allow_search=0,
            allow_browse=1,
            restrict_browsing_to_startup_directory=1,
            startup_directory_method='projects_url',
            force_close_on_insert=1,
            ),
        ),
    ))

for schema_key in agendaitem_schema.keys():
    if not agendaitem_schema[schema_key].schemata == 'default':
        agendaitem_schema[schema_key].widget.visible={'edit':'invisible',
                                                      'view':'invisible'}
agendaitem_schema['title'].required = False

class AgendaItemProject(BaseAgendaItem):
    """ We do not simply call it AgendaItem but AgendaItemProject
    to avoid confusion will AgendaItem in public part of the site.
    """
    security = ClassSecurityInfo()
    implements(IAgendaItemProject)

    _at_rename_after_creation = True
    schema = agendaitem_schema

    def post_validate(self, REQUEST, errors):
        if REQUEST.get('title', None) or REQUEST.get('project', None):
            return

        errors['title'] = _(u'label_title_needed',
                            default=u'You must specify a title if you do not select a project')

    def get_previous_project(self):
        try:
            previous_uid = self._previous_project
        except AttributeError:
            return

        uid_cat = getToolByName(self, 'uid_catalog')
        brains = uid_cat(UID = previous_uid)
        if len(brains) == 1:
            return brains[0].getObject()

    def set_previous_project(self, project):
        if project is None:
            self._previous_project = None
        else:
            self._previous_project = project.UID()

    @property
    def projects_url(self):
        portal = getSite()
        catalog = getToolByName(portal, 'portal_catalog')
        brains = catalog({'portal_type': 'ProjectContainer'})
        if len(brains) > 0:
            return brains[0].getURL().split(portal.absolute_url())[1]

        return '/'


atapi.registerType(AgendaItemProject, config.PROJECTNAME)
