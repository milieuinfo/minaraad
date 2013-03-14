# Utilitary views.
from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from plone.memoize.instance import memoize
from zope.interface import implements

from minaraad.projects.interfaces import IPASMemberView

empty_member_info = {
    'username': '', 'description': '', 'language': '',
    'home_page': '', 'name_or_id': '', 'location': '',
    'fullname': '', 'company': '', 'has_email': False}


class RolesInContext(BrowserView):
    """ Simple view used to check some data.
    Not declared in configure.zcml
    """
    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        user = mtool.getAuthenticatedMember()

        return '%s -> %s' % (user,
                             user.getRolesInContext(self.context))


class ParentRedirect(BrowserView):
    """ Redirects to the context parent.
    """
    def __call__(self):
        parent = aq_parent(aq_inner(self.context))
        if parent is None:
            parent = self.context

        return self.request.response.redirect(parent.absolute_url())


class PASMemberView(BrowserView):
    """Return 'harmless' info for a member.

    This code will be introduced in Plone 4.0 but we want it already.
    This replaces a few getMemberById calls in template code where it
    is not allowed in some contexts or review states.

    We have something extra:

    - show the company name

    - TODO Perhaps use first name plus fullname as fullname.

    Actually, we will combine the code from the PASMemberView and the
    getMemberInfo method that it gets most of its info from.
    """

    implements(IPASMemberView)

    @memoize
    def info(self, userid=None):
        context = aq_inner(self.context)
        pm = getToolByName(context, 'portal_membership')
        if not userid:
            member = pm.getAuthenticatedMember()
        else:
            member = pm.getMemberById(userid)
        if member is None:
            return self.get_empty_member_info(userid)
        return self.get_member_info(member)

    def get_member_info(self, member):
        names = [safe_unicode(member.getProperty('firstname', '')),
                 safe_unicode(member.getProperty('fullname'))]
        fullname = u' '.join([name for name in names if name])
        memberinfo = {'fullname': fullname,
                      'description': member.getProperty('description'),
                      'location': member.getProperty('location'),
                      'language': member.getProperty('language'),
                      'home_page': member.getProperty('home_page'),
                      'username': member.getUserName(),
                      'has_email': bool(member.getProperty('email')),
                      'company': member.getProperty('company', ''),
                      }
        memberinfo['name_or_id'] = memberinfo.get('fullname') or \
            memberinfo.get('username') or member.getUserId()
        return memberinfo

    def get_empty_member_info(self, userid):
        # No such member: removed?  We return something useful anyway.
        info = empty_member_info.copy()
        info['username'] = userid
        info['name_or_id'] = userid
        return info


class ParticipantMemberView(PASMemberView):
    """Return 'harmless' info for a participant.

    A participant can be a member or an extra invitee for who we only
    know a fullname and company.
    """

    implements(IPASMemberView)

    @memoize
    def info(self, userid=None):
        context = aq_inner(self.context)
        pm = getToolByName(context, 'portal_membership')
        if not userid:
            member = pm.getAuthenticatedMember()
        else:
            member = pm.getMemberById(userid)
        if member is not None:
            # Normal member
            return self.get_member_info(member)

        participants = context.get_invited_people()
        participant = participants.get(userid)
        if not participant:
            # No member, no participant.
            return self.get_empty_member_info(userid)
        # Participant.
        info = empty_member_info.copy()
        info['username'] = participant['id']
        info['name_or_id'] = participant['id']
        info['fullname'] = participant['fullname']
        info['company'] = participant.get('company', '')
        return info
