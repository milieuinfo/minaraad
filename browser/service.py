'''\
Service utilities

to be used by Manager only
'''

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.minaraad.config import TITLE_VOCAB

import logging
logger = logging.getLogger('Minaraad Service Utilities')


class ServiceUtils(BrowserView):

    members_deleted = None

    def __call__(self):
        if self.request.get('REQUEST_METHOD', 'GET').upper() == 'POST' \
                and self.request.get('form.button.DeleteMembers'):
            self.members_deleted = self.deleteMembersWithEmptyEmail()
        return self.index()

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
