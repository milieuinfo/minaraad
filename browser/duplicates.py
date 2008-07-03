from zope.cachedescriptors.property import Lazy

from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

import logging
logger = logging.getLogger('Minaraad email duplication')


class Duplication(BrowserView):

    message = None

    def __call__(self):
        if self.request.get('REQUEST_METHOD', 'GET').upper() == 'POST':
            if self.request.get('form.button.DeleteMember'):
                memberid = self.request.get('userid', '')
                self.message = self.deleteMember(memberid)
        return self.index()

    @Lazy
    def duplicates(self):
        context = aq_inner(self.context)
        portal_membership = getToolByName(context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        email = member.getProperty('email')
        members = portal_membership.listMembers()
        duplicates = [m for m in members if m.getProperty('email') == email]
        if len(duplicates) > 1:
            return duplicates
        return []

    def deleteMember(self, memberid):
        context = aq_inner(self.context)
        portal_membership = getToolByName(context, 'portal_membership')
        member_to_remove = portal_membership.getMemberById(memberid)
        if member_to_remove is None:
            return ("Member %s does not exist." % memberid)
        else:
            return ("We should remove member %s.  Not implemented yet" %
                    member_to_remove.getId())
