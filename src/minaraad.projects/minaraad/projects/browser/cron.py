# Pages that are not real pages, just called via cron.

import logging
from zope.i18n import translate
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from minaraad.projects import MinaraadProjectMessageFactory as _
from minaraad.projects.utils import send_email
from minaraad.projects.config import FROM_EMAIL

logger = logging.getLogger('minaraad.projects.browser.cron')


class ProjectsReminder(BrowserView):
    """ Sends an email to board members about the 'proposed' projects.
    """

    def get_projects(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        wft = getToolByName(self.context, 'portal_workflow')
        projects = []

        for brain in catalog({'portal_type': 'Project'}):
            try:
                project = brain.getObject()
            except:
                logger.info('Unable to wake object %s' % brain)
                continue

            if project.is_board_notified():
                # A mail has already been sent.
                continue

            if wft.getInfoFor(project, 'review_state') != 'in_consideration':
                # This project is not in the correct state.
                continue

            projects.append(project)

        return projects

    def get_board_member_ids(self):
        gtool = getToolByName(self.context, 'portal_groups')
        portal_props = getToolByName(self.context, 'portal_properties')

        governance_group_id = portal_props.minaraad_properties.governance_board
        governance_group = gtool.getGroupById(governance_group_id)

        if governance_group is None:
            msg = 'Daily governance board is set to be "%s", ' + \
                  'but this group does not exist'
            logger.info(msg % governance_group_id)
            return

        return governance_group.getGroupMemberIds()

    def __call__(self):
        projects = self.get_projects()
        member_ids = self.get_board_member_ids()
        mtool = getToolByName(self.context, 'portal_membership')

        logger.info("Running cron job for notifying of new projects.")
        if not projects or not member_ids:
            logger.info("No projects or no member ids.")
            return

        project_list = '\n'.join([' - %s: %s' % (p.Title(), p.absolute_url())
                                  for p in projects])

        mapping = {'fullname': '',
                   'project_list': project_list}

        for member_id in member_ids:
            member = mtool.getMemberById(member_id)
            mapping['fullname'] = member.getProperty('fullname', '')

            # We avoid potential problems with unicode.
            for key in mapping:
                mapping[key] = safe_unicode(mapping[key])

            title = translate(_(u'label_boardmember_digest_mail_title',
                                default=u'Weekly list of proposed projects',
                                mapping=mapping),
                              context=self.context.REQUEST)

            content = translate(_(u'label_boardmember_digestmail_content',
                              default=u'Dear ${fullname}, \n\n' + \
                              'Here is the list of the projects that have ' + \
                              'been proposed this week:\n' + \
                              '${project_list} \n\n' + \
                              'Best regards.',
                              mapping=mapping),
                            context=self.context.REQUEST)

            member_email = member.getProperty('email', None)
            if member_email is None:
                logger.info('No email found for board member %s' % member)

            send_email(member_email, FROM_EMAIL, title, content)

        # We mark the projects has notified.
        [p.mark_as_notified() for p in projects]
        logger.info("Ran cron job for notifying of new projects.")
