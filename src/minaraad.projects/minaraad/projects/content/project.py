from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent, aq_inner
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from minaraad.projects import MinaraadProjectMessageFactory as _
from minaraad.projects import config
from minaraad.projects.interfaces import IProject
from minaraad.projects.utils import prepend_zero
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone.app.blob.field import BlobField
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements
import transaction

try:
    from Products.minaraad.content.contacts import contacts_schema
    from Products.minaraad.content.themes import theme_schema
    from Products.minaraad.content.themes import ThemeMixin
    contacts_schema, theme_schema, ThemeMixin  # pyflakes
except ImportError:
    contacts_schema = atapi.Schema(())
    theme_schema = atapi.Schema(())
    ThemeMixin = object

project_schema = atapi.OrderedBaseFolderSchema.copy() + atapi.Schema((

    atapi.StringField(
        name='project_number',
        required=True,
        validators=('projectNumber3Digits', ),
        widget=atapi.StringWidget(
            label=_(u'label_project_number',
                    default=u'Project number')
        )
    ),

    atapi.StringField(
        name='product_number',
        required=False,
        validators=('projectNumber3Digits', ),
        widget=atapi.StringWidget(
            label=_(u'label_product_number',
                    default=u'Product number')
        )
    ),

    atapi.TextField(
        name='body',
        allowable_content_types=('text/html', ),
        default_content_type='text/html',
        default_output_type='text/html',
        widget=atapi.RichWidget(
            label=_(u'label_description',
                    default=u'Description'),
            description=_(
                u'desc_description',
                default=(u"A short description of the contents and the "
                         u"legal background of the advisory request.")),
        )
    ),

    atapi.DateTimeField(
        name='advisory_date',
        required=True,
        widget=atapi.CalendarWidget(
            show_hm=False,
            label=_(u'label_adv_date',
                    default=u'Advisory date')
        )
    ),

    atapi.StringField(
        name='advisory_requester',
        required=True,
        vocabulary='_requester_vocabulary',
        widget=atapi.SelectionWidget(
            label=_(u'label_adv_requester',
                    default=u'Advisory requester')
        )
    ),

    atapi.IntegerField(
        name='advisory_term',
        required=True,
        default=30,
        widget=atapi.IntegerWidget(
            label=_(u'label_adv_term',
                    default=u'Advisory term')
        )
    ),

    BlobField(
        name='advisory_request',
        widget=atapi.FileWidget(
            label=_(u'label_adv_request',
                    default=u'Advisory request')
        )
    ),

    atapi.LinesField(
        name='organisations',
        required=False,
        vocabulary='_organisation_vocabulary',
        widget=atapi.MultiSelectionWidget(
            format="checkbox",
            label=_(u'label_organisations',
                    default=u'Participating organisations')
        )
    ),

    atapi.StringField(
        name='responsible_group',
        required=True,
        vocabulary='_group_vocabulary',
        widget=atapi.SelectionWidget(
            label=_(u'label_responsible_group',
                    default=u'Responsible group')
        )
    ),


    atapi.DateTimeField(
        name='postponed_date',
        required=False,
        widget=atapi.CalendarWidget(
            show_hm=False,
            label=_(u'label_postpone_date',
                    default=u'Dealine (postponed)')
        )
    ),

    atapi.DateTimeField(
        name='delivery_date',
        required=False,
        widget=atapi.CalendarWidget(
            show_hm=False,
            label=_(u'label_delivery_date',
                    default=u'Delivery date (actual)')
        )
    ),


    atapi.StringField(
        name='advisory_type',
        required=True,
        vocabulary='_adv_type_vocabulary',
        widget=atapi.SelectionWidget(
            label=_(u'label_adv_type',
                    default=u'Advisory type')
        )
    ),

    atapi.LinesField(
        name='disagreeing_members',
        vocabulary='_disagreeing_members_vocabulary',
        widget=atapi.MultiSelectionWidget(
            label=_(u'label_disagreeing_members',
                    default=u'Disagreeing members'),
            format='checkbox',
        )
    ),

    atapi.LinesField(
        name='reject_reasons',
        widget=atapi.LinesWidget(
            label=_(u'label_reject_reasons',
                    default=u'Reject reasons')
        )
    ),

    atapi.LinesField(
        name='assigned_groups',
        required=True,
        vocabulary='_group_vocabulary',
        widget=atapi.InAndOutWidget(
            label=_(u'label_assigned_groups',
                    default=u'Assigned groups')
        )
    ),
)) + \
    theme_schema.copy() + \
    contacts_schema.copy()

project_schema['title'].widget.label = _(
    u'label_short_title',
    default=u'Short title')
project_schema['title'].widget.description = _(
    u'desc_short_title',
    default=u'Internal working title')
project_schema['description'].widget.label = _(
    u'label_full_title',
    default=u'Full title')
project_schema['description'].widget.description = _(
    u'desc_full_title',
    default=u'This is the official legal title from the advisory request')
project_schema['description'].schemata = 'default'

project_schema.moveField('project_number', before='title')

permission_mapping = {
    'minaraad.projects: manage new project fields': [
        'title',
        'description',
        'body',
        'advisory_date',
        'advisory_requester',
        'advisory_term',
        'advisory_request'],
    'minaraad.projects: manage in consideration project fields': [
        'organisations',
        'responsible_group',
        'assigned_groups',
        'theme',
        'coordinator',
        'authors'],
    'minaraad.projects: manage active project fields': ['postponed_date'],
    'minaraad.projects: manage finished project fields': [
        'delivery_date',
        'advisory_type',
        'disagreeing_members',
        'reject_reasons',
        'product_number'],
    'minaraad.projects: view project id': ['project_number']}

for perm, fields in permission_mapping.items():
    for field in fields:
        project_schema[field].write_permission = perm


for schema_key in project_schema.keys():
    if not project_schema[schema_key].schemata == 'default':
        project_schema[schema_key].widget.visible = {'edit': 'invisible',
                                                     'view': 'invisible'}


class Project(atapi.OrderedBaseFolder, ThemeMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(IProject)

    _at_rename_after_creation = True
    schema = project_schema

    security.declarePrivate('_renameAfterCreation')

    def _renameAfterCreation(self, check_auto_id=False):
        """ Use the project number and year to generate the ID.
        """
        project_number = self.getProject_number()
        year = self.getAdvisory_date().year()

        new_id = '%s-%s' % (year, project_number)

        invalid_id = False
        check_id = getattr(self, 'check_id', None)
        if check_id is not None:
            invalid_id = check_id(new_id, required=1)
        else:
            parent = aq_parent(aq_inner(self))
            invalid_id = new_id in parent.objectIds()

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

    def _adv_type_vocabulary(self):
        return atapi.DisplayList([
            ('unanimous', _(u'label_unanimous',
                            default=u'Unanimous')),
            ('abstention_rejection',
             _(u'label_abstention_rejection',
               default=u'Abstention and/or reject points'))])

    def _members_vocabulary(self):
        return atapi.DisplayList(
            sorted([(m['id'], m['fullname'])
                    for m in self.get_board_members()],
                   key=lambda x: x[0]))

    def _disagreeing_members_vocabulary(self):
        props = getToolByName(self, 'portal_properties').minaraad_properties
        terms = props.getProperty('membership_organizations', [])
        return atapi.DisplayList([(term, term) for term in terms if term])

    def _organisation_vocabulary(self):
        catalog = getToolByName(self, 'portal_catalog')
        return atapi.DisplayList(
            [(o.id, o.Title) for o in catalog({
                'portal_type': 'Organisation'})])

    def _requester_vocabulary(self):
        props = getToolByName(self, 'portal_properties').minaraad_properties
        terms = props.getProperty('requesters', [])
        return atapi.DisplayList([(term, term) for term in terms if term])

    def get_meetings(self):
        """ Returns the meetings linked to the project.
        """
        brefs = self.getBRefs('discussedProjects')
        mtool = getToolByName(self, 'portal_membership')
        for meeting in self.get_agenda_items().keys():
            if meeting in brefs:
                continue
            if mtool.checkPermission('View', meeting):
                brefs.append(meeting)
        return sorted(brefs, key=lambda x: x.getStart_time())

    def get_documents(self):
        """ Returns the list of documents added to the project.
        """
        return sorted(self.contentValues(),
                      key=lambda x: x.Title())

    def getPID(self):
        """ Returns the advisory date displayed
        as YYYYMMDD.
        """
        d = self.getAdvisory_date()
        if d is None:
            return ''

        return '%s%s%s' % (d.year(),
                           prepend_zero(d.month()),
                           prepend_zero(d.day()))

    def get_deadline(self):
        """ Returns advisory date + advisory term.
        """
        postponed = self.getPostponed_date()
        if postponed is not None:
            return postponed

        try:
            return self.getAdvisory_date() + self.getAdvisory_term()
        except:
            # One of the data might not be set.
            pass

    def _get_annotations(self):
        """ Returns the Annotations linked to the project.
        If they do not exists, it creates them.
        """
        anno_key = 'minaraad.projects'
        annotations = IAnnotations(self)

        metadata = annotations.get(anno_key, None)
        if metadata is None:
            annotations[anno_key] = PersistentDict()
            metadata = annotations[anno_key]

        return metadata

    def _get_agenda_items(self):
        """ Returns a PersistentDict, where
        keys are the meetings UIDS and values
        are the list of items UIDs belonging to
        this meeting are referencing the project.
        """
        anno = self._get_annotations()

        if 'agenda_items' not in anno:
            anno['agenda_items'] = PersistentDict()

        return anno['agenda_items']

    def get_agenda_items(self):
        """ Transforms the dictionnary produced by
        _get_agenda_items to a dictionnary with the meetings
        and items instead of the UIDs.
        """
        items = self._get_agenda_items()
        uid_cat = getToolByName(self, 'uid_catalog')

        def object_from_uid(uid):
            brains = uid_cat(UID=uid)
            if len(brains) == 1:
                return brains[0].getObject()

        res = {}
        for meeting_uid in items.keys():
            meeting = object_from_uid(meeting_uid)
            if meeting is None:
                continue

            res[meeting] = []
            for item_uid in items[meeting_uid]:
                item = object_from_uid(item_uid)
                if item is None:
                    continue
                res[meeting].append(item)

        return res

    def add_agendaitem_reference(self, agendaitem):
        items = self._get_agenda_items()
        meeting_uid = aq_parent(aq_inner(agendaitem)).UID()
        agendaitem_uid = agendaitem.UID()

        if meeting_uid not in items:
            items[meeting_uid] = PersistentList()

        if agendaitem_uid not in items[meeting_uid]:
            items[meeting_uid].append(agendaitem_uid)

    def remove_agendaitem_reference(self, agendaitem):
        items = self._get_agenda_items()
        meeting_uid = aq_parent(aq_inner(agendaitem)).UID()
        agendaitem_uid = agendaitem.UID()

        if meeting_uid not in items:
            # That should not happen normally ...
            return

        if agendaitem_uid not in items[meeting_uid]:
            # That should not happen neither.
            return

        items[meeting_uid].remove(agendaitem_uid)

        if len(items[meeting_uid]) == 0:
            del items[meeting_uid]

    def get_board_members(self):
        anno = self._get_annotations()
        if anno.get('board_members', None) is None:
            anno['board_members'] = PersistentList()

        return anno['board_members']

    def is_board_notified(self):
        """ Tells if a cron mail has already been sent to
        the board members.
        """
        anno = self._get_annotations()
        return anno.get('notified_to_board', False)

    def mark_as_notified(self):
        """ Notifies that a mail has been sent to the board.
        """
        anno = self._get_annotations()
        anno['notified_to_board'] = True

    def get_advisory_type(self):
        """ Returns the nice/translatable version.
        """
        adv = self.getAdvisory_type()
        vocab = dict(self._adv_type_vocabulary().items())

        return vocab.get(adv, None)

    def get_public_advisory(self):
        advisories = self.getBRefs(relationship='related_project')
        if not advisories:
            return
        advisory = advisories[0]
        mtool = getToolByName(self, 'portal_membership')
        if mtool.checkPermission('View', advisory):
            return advisory


atapi.registerType(Project, config.PROJECTNAME)
