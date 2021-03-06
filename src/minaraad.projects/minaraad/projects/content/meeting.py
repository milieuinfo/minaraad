import logging

from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent, aq_inner
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.Archetypes import atapi
from Products.Archetypes.event import ObjectEditedEvent
from Products.CMFCore.utils import getToolByName
from Products.DataGridField.DataGridField import DataGridField
from Products.DataGridField.DataGridWidget import DataGridWidget
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.component.hooks import getSite
from zope.event import notify
from zope.interface import implements
import transaction

from minaraad.projects import MinaraadProjectMessageFactory as _
from minaraad.projects import config
from minaraad.projects.interfaces import IMeeting, IAgendaItem
from minaraad.projects.utils import prepend_zero
from minaraad.projects.widgets import PARTICIPANT_ABSENT
from minaraad.projects.widgets import ParticipantsWidget

from base_meeting import base_meeting_schema, BaseMeeting

logger = logging.getLogger(__name__)

meeting_schema = base_meeting_schema.copy() + atapi.Schema((
    atapi.StringField(
        name='responsible_group',
        required=True,
        vocabulary='_group_vocabulary',
        widget=atapi.SelectionWidget(
            format='select',
            label=_(u'label_type',
                    default=u'Type')
        )
    ),

    atapi.TextField(
        name='body',
        allowable_content_types=('text/html', ),
        default_content_type='text/html',
        default_output_type='text/html',
        widget=atapi.RichWidget(
            label=_(u'label_description',
                    default=u'Description')
        )
    ),

    atapi.ReferenceField(
        name='meetinglocation',
        relationship='meetingLocation',
        multiValued=0,
        languageIndependent=1,
        allowed_types=('Organisation', ),
        widget=ReferenceBrowserWidget(
            label=_('label_location',
                    default='Location'),

            allow_search=0,
            allow_browse=1,
            base_query={
                'sort_on': 'sortable_title',
            },
            restrict_browsing_to_startup_directory=0,
            startup_directory_method='organisations_url',
            force_close_on_insert=1,
        ),
    ),

    atapi.StringField(
        name='roomNumber',
        required=False,
        widget=atapi.StringWidget(
            label=_(u'label_room_number',
                    default=u'Room number')
        )
    ),

    atapi.LinesField(
        name='invited_groups',
        vocabulary='_group_vocabulary',
        widget=atapi.InAndOutWidget(
            label=_(u'label_assigned_groups',
                    default=u'Assigned groups')
        )
    ),

    atapi.LinesField(
        name='participants',
        vocabulary='_participants_vocabulary',
        widget=ParticipantsWidget(
            label=_(u'label_participants_attendance',
                    default=u'Participants attendance')
        )
    ),

    DataGridField(
        name='otherInvitees',
        default=({'id': 'name',
                  'title': _(u'Name')},
                 {'id': 'company',
                  'title': _(u'Company')},
                 ),
        widget=DataGridWidget(
            label=_(u'label_other_invitees',
                    default=u"Other invitees"),
            description=_(
                u'help_other_invitees',
                default=(u"Enter the invitees who are not in the selected "
                         u"committees.")),
            column_names=(_(u'Name'), _(u'Company')),
        ),
        allow_reorder=False,
        required=False,
        validators=('isDataGridFilled', ),
        columns=('name', 'company', )
    ),

))

for schema_key in meeting_schema.keys():
    if not meeting_schema[schema_key].schemata == 'default':
        meeting_schema[schema_key].widget.visible = {'edit': 'invisible',
                                                     'view': 'invisible'}
    meeting_schema[schema_key].write_permission = \
        'minaraad.projects: manage non past meetings fields'

meeting_schema['participants'].write_permission = \
    'minaraad.projects: manage past meetings fields'
meeting_schema['title'].widget.visible = {'edit': 'invisible',
                                          'view': 'invisible'}
meeting_schema['title'].required = False
meeting_schema.moveField('responsible_group', before='start_time')


class Meeting(BaseMeeting):
    """Meeting.
    """
    security = ClassSecurityInfo()
    implements(IMeeting)

    _at_rename_after_creation = True
    schema = meeting_schema

    security.declarePrivate('_renameAfterCreation')

    def _renameAfterCreation(self, check_auto_id=False):
        """ Use the project number and year to generate the ID.
        """
        start_time = self.getStart_time()
        formated_time = '%s%s%s' % (start_time.year(),
                                    prepend_zero(start_time.month()),
                                    prepend_zero(start_time.day()))

        parent = aq_parent(aq_inner(self))
        new_id = formated_time
        count = 0

        while new_id in parent.objectIds():
            new_id = '%s-%s' % (formated_time, count)
            count += 1

        invalid_id = False
        check_id = getattr(self, 'check_id', None)
        if check_id is not None:
            invalid_id = check_id(new_id, required=1)

        if not invalid_id:
            # Can't rename without a subtransaction commit when using
            # portal_factory!
            transaction.savepoint()
            self.setId(new_id)
            return new_id

        return False

    def _group_vocabulary(self):
        """ List the groups available.
        """
        portal_groups = getToolByName(self, 'portal_groups')
        return atapi.DisplayList(
            [(g['id'], g['title']) for g in portal_groups.searchGroups()
             if not g['id'] in config.FILTERED_GROUPS])

    def _participants_vocabulary(self):
        """ List the participants for a meeting.
        See projects.minaraad.events.save_invited to see
        how the list is generated.
        """
        participants = self.get_invited_people()
        return atapi.DisplayList(
            sorted([(p['id'], p['fullname']) for p in participants.values()],
                   key=lambda x: x[1]))

    @property
    def organisations_url(self):
        """ Returns URL of the DigiBib containing the meeting.
        """
        portal = getSite()
        catalog = getToolByName(portal, 'portal_catalog')
        brains = catalog({'portal_type': 'OrganisationContainer'})
        if len(brains) > 0:
            return brains[0].getURL().split(portal.absolute_url())[1]

        return '/'

    def get_all_projects(self):
        """ Returns the projects linked by the meeting and
        the ones linked by the items.
        """
        projects = []
        for item in self.find_items():
            try:
                item = item.getObject()
            except:
                continue

            p = item.getProject()
            if p:
                projects.append(p)
        return projects

    def project_numbers(self):
        # Used in the catalog.
        return [p.getProject_number() for p in self.get_all_projects()]

    def get_files(self):
        """ Finds all attachment for the meeting.
        """
        return [o.getObject() for o in self.get_file_brains()]

    def get_file_brains(self):
        """ Finds attachment brains for the meeting.

        We only want attachments that are directly in the meeting
        itself, so not in any children.
        """
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog({
            'path': {'query': '/'.join(self.getPhysicalPath()), 'depth': 1},
            'portal_type': 'FileAttachment'})

        return sorted(brains, key=lambda x: x.Title)

    def _get_annotations(self):
        """ Returns the Annotations linked to the meeting.
        If they do not exists, it creates them.
        """
        anno_key = 'minaraad.projects'
        annotations = IAnnotations(self)

        metadata = annotations.get(anno_key, None)
        if metadata is None:
            annotations[anno_key] = PersistentDict()
            metadata = annotations[anno_key]

        return metadata

    def _empty_invited_people(self):
        anno = self._get_annotations()
        anno['invited_people'] = PersistentDict()

    def get_invited_people(self):
        anno = self._get_annotations()
        if anno.get('invited_people', None) is None:
            anno['invited_people'] = PersistentDict()

        return anno['invited_people']

    def get_saved_location(self):
        anno = self._get_annotations()
        if anno.get('saved_location', None) is None:
            anno['saved_location'] = PersistentDict()

        return anno['saved_location']

    def manage_delObjects(self, ids, *args, **kwargs):
        """ When an AgendaItem is deleted, we have to delete the reference
        to the meeting in the referenced project.
        """
        if isinstance(ids, basestring):
            ids = [ids]

        for agenda_id in ids:
            item = self[agenda_id]

            if not IAgendaItem.providedBy(item):
                # That's not an item.
                continue

            project = item.getProject()
            if project is None:
                continue
            project.remove_agendaitem_reference(item)

        base = super(Meeting, self).manage_delObjects(ids, *args, **kwargs)
        self._update_agenda_item_attachment_counter()
        return base

    def _notify_item_modification(self, item):
        if item and IAgendaItem.providedBy(item):
            item.setProject(item.get_previous_project())
            notify(ObjectEditedEvent(aq_inner(item)))

    def _update_agenda_item_attachment_counter(self):
        """ Updates the 'attachment_start' attribute on agenda items.
        """
        att_count = 1
        catalog = getToolByName(self, 'portal_catalog')
        items = self.find_items_and_times()

        for it in items:
            item = it[0].getObject()
            # Avoid making a change to the database when the count
            # stays the same.
            if getattr(item, 'attachment_start', None) != att_count:
                item.attachment_start = att_count
            # Only update the main attachment count when this agenda
            # item has at least one attachment.
            attachments = catalog.searchResults(
                portal_type='FileAttachment',
                path='/'.join(item.getPhysicalPath()))
            if attachments:
                att_count += 1

    def manage_pasteObjects(self, *args, **kwargs):
        """ We override the manage_pasteObjects() so we can
        notify modification on all items and so update
        linked projects.
        """
        base = super(Meeting, self).manage_pasteObjects(*args, **kwargs)
        for obj in base:
            item = self[obj['new_id']]
            self._notify_item_modification(item)

        self._update_agenda_item_attachment_counter()
        return base

    def manage_clone(self, *args, **kwargs):
        """ We override manage_clone for the same reason we overriden
        manage_pasteObjects
        """
        cloned = super(Meeting, self).manage_clone(*args, **kwargs)
        self._notify_item_modification(cloned)

        self._update_agenda_item_attachment_counter()
        return cloned

    def getParticipants(self):
        """ Returns a list of tuples (participant_name, status).
        """
        participants = []
        for p in self.getField('participants').getRaw(self):
            p_split = p.split('|')
            if len(p_split) == 1:
                participants.append((p, PARTICIPANT_ABSENT))
            elif len(p_split) == 2:
                try:
                    participants.append(('|'.join(p_split[:-1]),
                                         int(p_split[-1])))
                except (ValueError, AttributeError):
                    logger.warn("Ignoring bad value for participant: %r", p)
            else:
                pass

        return participants

    def setParticipants(self, participants):
        """ Works the other way around: expects a list of tuples
        and transforms it into a list of strings.
        """
        value = ['|'.join(p) for p in participants]
        self.getField('participants').set(self, value)


atapi.registerType(Meeting, config.PROJECTNAME)
