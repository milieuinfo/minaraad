import logging
from zope.app.component.hooks import getSite
from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from zope.i18n import translate
from Products.CMFPlone.utils import safe_unicode
from persistent.dict import PersistentDict

from minaraad.projects.content.base_meeting import BaseMeeting
from minaraad.projects import MinaraadProjectMessageFactory as _
from minaraad.projects.utils import send_email
from minaraad.projects.config import FROM_EMAIL
from minaraad.projects.interfaces import IAgendaItemProject

logger = logging.getLogger('minaraad.projects.events')


def set_agenda_item_order(item, event):
    """ This event is called when an AgendaItem is added to a meeting.
    It will set the order so the item will be the last of the list.
    """
    meeting = aq_parent(item)
    if meeting is None or item.getOrder() is not None:
        return

    items = meeting.find_items()
    if items:
        item.setOrder(len(items) - 1)
    else:
        item.setOrder(0)

def save_invited(meeting, event):
    """ When a meeting is saved, we store the list
    of participants based on the groups.
    We do so to have a copy of the participants when the meeting
    was created and get no impact we people leave/join an
    invited group.

    When the meeting is edited, we might add new members to the list,
    but we never delete any member of the list.
    """
    invited = meeting.get_invited_people()
    portal_groups = getToolByName(meeting, 'portal_groups')

    all_groups = list(meeting.getInvited_groups()) + \
                 [meeting.getResponsible_group()]

    for group_id in all_groups:
        group = portal_groups.getGroupById(group_id)

        for member in group.getGroupMembers():
            # Hum, we have some confusion here between getUserName
            # (login name) and getId (user id).  This is usually the
            # same, but not necessarily so for us as we use
            # collective.emaillogin.
            member_id = member.getId()
            if member_id in invited:
                # This member is already in the list.
                continue

            invited[member_id] = PersistentDict()
            invited[member_id]['id'] = member_id
            invited[member_id]['fullname'] = member.getProperty('fullname', '')
            invited[member_id]['email'] = member.getProperty('email', '')

def concatenate_pdf(attachment, event):
    """ When a SimpleAttachment file is created, so check if it was created
    in an AgendaItem of a Meeting.
    If it is the case, we update the PDF for file that contains all files of
    the meeting.
    """
    meeting = aq_parent(aq_parent(attachment))
    if not isinstance(meeting, BaseMeeting):
        # We are not in one of our custom meetings.
        return

    f = attachment.getFile()
    if not f.content_type == 'application/pdf':
        # Ok, that not a PDF, we can not use it.
        return

    meeting.generate_pdf()


def save_project_references(agendaitem, event):
    """ An agenda item can reference a project via the 'project'
    attribute.
    To avoid having to look at all back references to find the meetings
    where a project is discussed, we update a persistent dictionnary
    in the project to quickly find the meeting.
    """
    # We first look at the previous project linked
    # by the Agenda item.
    previous_project = agendaitem.get_previous_project()
    current_project = agendaitem.getProject()

    if previous_project:
        previous_project.remove_agendaitem_reference(agendaitem)

    if current_project:
        current_project.add_agendaitem_reference(agendaitem)

    agendaitem.set_previous_project(current_project)


def save_board_members(project, event):
    """ Saves the list of board member after creating a project.
    """
    wft = getToolByName(getSite(), 'portal_workflow')
    if wft.getInfoFor(project, 'review_state') != 'in_consideration':
        return

    portal_groups = getToolByName(getSite(), 'portal_groups')
    members = project.get_board_members()

    all_groups = list(project.getAssigned_groups()) + \
                 [project.getResponsible_group()]
    m_ids = [m['id'] for m in members]

    for group_id in all_groups:
        group = portal_groups.getGroupById(group_id)
        g_tuple = (group.id, group.title_or_id())

        for member in group.getGroupMembers():
            member_id = member.getId()
            fullname = member.getProperty('fullname', '')
            company = member.getProperty('company', '')
            if member_id in m_ids:
                for m in members:
                    if m['id'] != member_id:
                        continue
                    if not g_tuple in m['groups']:
                        m['groups'].append(g_tuple)
                    if m.get('fullname') != fullname:
                        m['fullname'] = fullname
                    if m.get('company') != company:
                        m['company'] = company
                    break
                continue

            m_ids.append(member_id)

            memberd = PersistentDict()
            memberd['id'] = member_id
            memberd['fullname'] = fullname
            memberd['company'] = company
            memberd['groups'] = [g_tuple]
            members.append(memberd)


def copy_project_title(agendaItem, event):
    """ When an agenda item is saved, if no title is providen, then
    we use the project's title (if existing)
    """
    if agendaItem.title or not agendaItem.getProject():
        return

    agendaItem.title = agendaItem.getProject().title


def send_email_to_secretary(project, event):
    """ Sends a mail to the secretary when a project needs to be checked.
    """
    # We first check the project is in the correct state.
    wft = getToolByName(getSite(), 'portal_workflow')
    if wft.getInfoFor(project, 'review_state') != 'in_verification':
        return

    # We find the secretary address.
    portal_props = getToolByName(project, 'portal_properties')
    secretary_email = portal_props.minaraad_properties.secretary_email

    mapping = {'project_name': project.Title(),
               'project_url': project.absolute_url()}

    for key in mapping:
        mapping[key] = safe_unicode(mapping[key])

    title = translate(
        _(u'label_secretary_mail_title',
          default=u'Project ${project_name} has been proposed',
          mapping=mapping),
        context=project.REQUEST)

    content = translate(
        _(u'label_secretary_mail_content',
          default=(u"The project ${project_name} has to be verified.\n"
                   u"The project can be found here: ${project_url}"),
          mapping=mapping),
        context=project.REQUEST)

    send_email(secretary_email, FROM_EMAIL, title, content)


def send_email_to_board(project, event):
    """ When a project reaches the 'proposed_to_board' state,
    an email is sent to all board members.
    """
    # We first check the project is in the correct state.
    wft = getToolByName(project, 'portal_workflow')
    if wft.getInfoFor(project, 'review_state') != 'in_consideration':
        return

    # We find the secretary address.
    portal_props = getToolByName(project, 'portal_properties')
    secretary_email = portal_props.minaraad_properties.secretary_email

    mtool = getToolByName(project, 'portal_membership')
    gtool = getToolByName(project, 'portal_groups')
    portal_props = getToolByName(project, 'portal_properties')

    governance_group_id = portal_props.minaraad_properties.governance_board
    governance_group = gtool.getGroupById(governance_group_id)

    if governance_group is None:
        msg = 'Daily governance board is set to be "%s", ' + \
              'but this group does not exist'
        logger.info(msg % governance_group_id)
        return

    mapping = {'fullname': '',
               'project_name': project.Title(),
               'project_desc': project.Description(),
               'project_url': project.absolute_url()}

    for member_id in governance_group.getGroupMemberIds():
        member = mtool.getMemberById(member_id)
        mapping['fullname'] = member.getProperty('fullname', '')

        # We avoid potential problems with unicode.
        for key in mapping:
            mapping[key] = safe_unicode(mapping[key])

        title = translate(
            _(u'label_boardmember_mail_title',
              default=u'Project ${project_name} has been proposed',
              mapping=mapping),
            context=project.REQUEST)

        content = translate(
            _(u'label_boardmember_mail_content',
              default=(
                  u'Dear ${fullname}, \n\n'
                  u'The project ${project_name} has been proposed to the '
                  u'board. Here is the description of the project: \n\n'
                  u'${project_desc}\n\n'
                  u'More information can be found here: \n\n${project_url}'),
              mapping=mapping),
            context=project.REQUEST)

        member_email = member.getProperty('email', None)
        if member_email is None:
            logger.info('No email found for board member %s' % member)

        send_email(member_email, secretary_email, title, content)


def save_meeting_location(meeting, event):
    """ When a meeting is saved, we copy the location information
    so it is not updated if the Organisation object is updated.
    """
    location = meeting.getMeetinglocation()
    if not location:
        return

    saved_location = meeting.get_saved_location()
    if 'saved' in saved_location:
        return

    saved_location['saved'] = True
    saved_location['address'] = location.getAddress()
    saved_location['postalCode'] = location.getPostalCode()
    saved_location['city'] = location.getCity()


def update_attachment_counter(attachment, event):
    """ When an attachment is saved in an AgendaItem project,
    we check if it's a new one.
    In that case, we update the attachment numbering.
    """
    agenda_item = aq_parent(attachment)
    if agenda_item is None or not IAgendaItemProject.providedBy(agenda_item):
        # The attachment has not been saved yet, or not in an agenda item.
        return

    catalog = getToolByName(attachment, 'portal_catalog')
    att_count = len(catalog.searchResults(
        portal_type = 'FileAttachment',
        path = '/'.join(agenda_item.getPhysicalPath())))

    try:
        old_att_count = agenda_item.attachment_count
    except AttributeError:
        old_att_count = 0

    if old_att_count != att_count:
        aq_parent(aq_inner(agenda_item))._update_agenda_item_attachment_counter()
