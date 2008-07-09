'''\
Service utilities

to be used by Manager only
'''

from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.minaraad.config import TITLE_VOCAB

import logging
logger = logging.getLogger('Minaraad Service Utilities')


class ServiceUtils(BrowserView):

    members_deleted = None
    double_emails = None

    def __call__(self):
        if self.request.get('REQUEST_METHOD', 'GET').upper() == 'POST':
            if self.request.get('form.button.DeleteMembers'):
                self.members_deleted = self.deleteMembersWithEmptyEmail()
            if self.request.get('form.button.FindDoubleEmails'):
                self.double_emails = self.find_double_emails()
        return self.index()

    def find_double_emails(self):
        context = aq_inner(self.context)
        portal_membership = getToolByName(context, 'portal_membership')
        members = portal_membership.listMembers()
        emails = {}
        for member in members:
            email = member.getProperty('email')
            if emails.get(email) is None:
                emails[member.getProperty('email')] = []
            emails[member.getProperty('email')].append(member.getId())

        return [(email, ids) for (email, ids) in emails.items()
                if len(ids) > 1]

    def deleteMembersWithEmptyEmail(self):
        'Delete all members with no email address'
        mt = getToolByName(self, 'portal_membership')
        acl = getToolByName(self, 'acl_users')
        all_members = mt.listMembers()
        members_without_email = [m for m in all_members
                                 if not m.getProperty('email')
                                 or not '@' in m.getProperty('email')]

        logger.info('Found %i members without email, proceed to delete...' %
                    (len(members_without_email), ))
        for member in members_without_email:
            id = member.getId()
            logger.info('Deleting member "%s"' % (id, ))
            acl.userFolderDelUsers([id])
        logger.info('Finished deleting %i members' %
                    (len(members_without_email), ))
        return 'Deleted %i members' % (len(members_without_email), )

    def resetMemberDataTitle(self):
        'Overwrite the title selection for members in the memberdata'
        md = getToolByName(self, 'portal_memberdata')
        # special care for our selection property gender
        md._updateProperty('genders', TITLE_VOCAB)
        logger.info('"Genders" property of memberdata tool is reset.')
        return '"Genders" property of memberdata tool is reset.'

    def addMemberDataLastModification(self):
        'add last_modification_date to the memberdata'
        md = getToolByName(self, 'portal_memberdata')
        if 'last_modification_date' not in md.propertyIds():
            md.manage_addProperty('last_modification_date', '2000/01/01',
                                  'date')
        msg = '"last_modification_date" property of memberdata tool is added.'
        logger.info(msg)
        return msg

    def modified_members(self):
        """Return a list of members that have (recently) been modified.

        XXX Not used yet!  An offer has been made to implement this.
        The current lines are copied from a quick try with a zopectl
        debug session and will not work.
        """
        if True:
            return "Not implemented yet."
        from DateTime import DateTime
        memship = app.minaraad.portal_membership
        members = memship.listMembers()
        changed_members = [m for m in members if m.getProperty('last_modification_date') != DateTime('2000/01/01')]
        len(changed_members)

        info = [(m.getProperty('last_modification_date').strftime('%Y-%m-%d'), m.getId()) for m in changed_members]
        for d, n in info: print d, n
