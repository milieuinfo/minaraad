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
                context = aq_inner(self.context)
                portal_membership = getToolByName(context, 'portal_membership')
                member = portal_membership.getAuthenticatedMember()
                redirect = False
                if member.id == memberid:
                    # We will delete ourselves.
                    portal_url = getToolByName(
                        context, 'portal_url').getPortalObject().absolute_url()
                    # Choose the first other member id as the new id
                    # to login as.
                    new_id = [m.id for m in self.duplicates
                              if m.id != memberid][0]
                    redirect = portal_url + '/login_form?login_name=' + new_id
                self.message = self.deleteMember(memberid)
                if redirect:
                    self.request.response.redirect(redirect)
                    return ""
        return self.index()

    @Lazy
    def duplicates(self):
        context = aq_inner(self.context)
        portal_membership = getToolByName(context, 'portal_membership')
        portal = getToolByName(context, 'portal_url').getPortalObject()
        if portal_membership.isAnonymousUser() or \
                portal_membership.checkPermission('Manage Users', portal):
            # An anonymous user may be busy with a password reset,
            # which will land him here with a userid in the request.
            member_id = self.request.get('userid', '')
            member = portal_membership.getMemberById(member_id)
        else:
            member = portal_membership.getAuthenticatedMember()
        if member is None:
            return []
        email = member.getProperty('email')
        members = portal_membership.listMembers()
        duplicates = [m for m in members if m.getProperty('email') == email]
        if len(duplicates) > 1:
            return duplicates
        return []

    def deleteMember(self, member_id):
        """Delete a member.
        """
        context = aq_inner(self.context)
        portal_membership = getToolByName(context, 'portal_membership')
        if portal_membership.isAnonymousUser():
            return "You need to be logged in."

        member_to_remove = portal_membership.getMemberById(member_id)
        if member_to_remove is None:
            return ("Member %s does not exist." % member_id)
        # Normal users are not allowed to call
        # portal_membership.deleteMembers as that needs the
        # "Manage Users" permission.  So we need to duplicate the
        # relevant lines from that method here.  But we need to be
        # careful: as non-Manager you should only be allowed to
        # delete yourself or someone with the same email address.
        member = portal_membership.getAuthenticatedMember()
        own_email = member.getProperty('email')
        other_email = member_to_remove.getProperty('email')
        portal = getToolByName(context, 'portal_url').getPortalObject()
        if own_email != other_email and \
                not portal_membership.checkPermission('Manage Users', portal):
            return "Not allowed to remove this member"

        # Delete the user:
        acl = portal_membership.acl_users
        acl.userFolderDelUsers([member_id])

        # Delete the member's home folder.
        portal_membership.deleteMemberArea(member_id)

        # Delete the member's local roles.
        portal_membership.deleteLocalRoles(
            portal, [member_id], reindex=1, recursive=1)

        return ("Gebruiker %s verwijderd." % member_id)
