from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent, aq_inner
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from minaraad.projects import MinaraadProjectMessageFactory as _
from minaraad.projects import config
from minaraad.projects.content.base_agendaitem import BaseAgendaItem
from minaraad.projects.content.base_agendaitem import base_agendaitem_schema
from minaraad.projects.interfaces import IAgendaItemProject
from zope.component.hooks import getSite
from zope.interface import implements

agendaitem_schema = base_agendaitem_schema + atapi.Schema((
    atapi.TextField(
        name='summary',
        # Note: see process_form in browser/agenda_item.py where we
        # explicitly set the mimetype to text/html to avoid problems
        # when editing an empty text field.
        allowable_content_types=('text/html', ),
        default_content_type='text/html',
        default_output_type='text/html',
        widget=atapi.RichWidget(
            label=_(u'label_description',
                    default=u'Description')
        )
    ),

    atapi.ReferenceField(
        name='project',
        relationship='discussedProject',
        multiValued=0,
        languageIndependent=1,
        allowed_types=('Project', ),
        widget=ReferenceBrowserWidget(
            label=_('label_project',
                    default='Project'),
            only_for_review_states=('active', ),
            show_review_state=0,
            allow_search=0,
            allow_browse=0,
            show_results_without_query=1,
            base_query={'review_state': 'active'},
            restrict_browsing_to_startup_directory=0,
            force_close_on_insert=1,
        ),
    ),

    atapi.BooleanField(
        # This field will be set to false once the object has been saved
        # with @@edit_eganda_item view.
        # If set to True, it will be deleted by the default meeting view.
        name='in_factory',
        default=False,
        widget=atapi.BooleanWidget(
            visible={'edit': 'invisible', 'view': 'invisible'},
        ),
    ),
))

for schema_key in agendaitem_schema.keys():
    if not agendaitem_schema[schema_key].schemata == 'default':
        agendaitem_schema[schema_key].widget.visible = {'edit': 'invisible',
                                                        'view': 'invisible'}
agendaitem_schema['title'].required = False


class AgendaItemProject(BaseAgendaItem):
    """ We do not simply call it AgendaItem but AgendaItemProject
    to avoid confusion will AgendaItem in public part of the site.
    """
    security = ClassSecurityInfo()
    implements(IAgendaItemProject)

    _at_rename_after_creation = True
    schema = agendaitem_schema

    is_agenda_item_project = True

    def post_validate(self, REQUEST, errors):
        if REQUEST.get('title', None) or REQUEST.get('project', None):
            return

        errors['title'] = _(
            u'label_title_needed',
            default=u'You must specify a title if you do not select a project')

    def get_previous_project(self):
        try:
            previous_uid = self._previous_project
        except AttributeError:
            return

        uid_cat = getToolByName(self, 'uid_catalog')
        brains = uid_cat(UID=previous_uid)
        if len(brains) == 1:
            return brains[0].getObject()

    def set_previous_project(self, project):
        if project is None:
            self._previous_project = None
        else:
            self._previous_project = project.UID()

    def _update_numbering(self):
        meeting = aq_parent(aq_inner(self))
        meeting._update_agenda_item_attachment_counter()

    def manage_delObjects(self, ids, *args, **kwargs):
        """ When attachments are deleted in the agenda item,
        we have to update numbering.
        """
        base = super(AgendaItemProject, self).manage_delObjects(ids, *args,
                                                                **kwargs)
        self._update_numbering()
        return base

    def manage_pasteObjects(self, *args, **kwargs):
        """ When attachment items are pasted, we update numbering.
        """
        base = super(AgendaItemProject, self).manage_pasteObjects(*args,
                                                                  **kwargs)
        self._update_numbering()
        return base

    def manage_clone(self, *args, **kwargs):
        """ We override manage_clone for the same reason we overriden
        manage_pasteObjects.
        """
        base = super(AgendaItemProject, self).manage_clone(*args, **kwargs)
        self._update_numbering()
        return base

atapi.registerType(AgendaItemProject, config.PROJECTNAME)
