import urllib
from zope.interface import Interface, implements, Attribute
from configlets import AbstractView
from Products.CMFCore.utils import getToolByName
from Products.minaraad.interfaces import IAttendeeManager

class IAttendeesManagerView(Interface):

    def register():
        pass
    
    def unregister():
        pass
    
    def isRegistered():
        pass


import logging
class AttendeesManagerView(AbstractView):
    implements(IAttendeesManagerView)

    def __init__(self, *args, **kwargs):
        AbstractView.__init__(self, *args, **kwargs)

        self.manager = IAttendeeManager(self.context)
        
    def __call__(self):
        memberTool = getToolByName(self.context, 'portal_membership')
        isAnonymous = memberTool.isAnonymousUser()
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        response = self.request.response

        if isAnonymous:
            return response.redirect(portal.absolute_url() \
                   +"/login_form?came_from=" \
                   +urllib.quote(self.referring_url))

        action = getattr(self.request, 'form.button.Submit', None)
        member = memberTool.getAuthenticatedMember()
        if action == 'register':
            self.manager.addMember(member)
            return response.redirect(self.referring_url+"?portal_status_message=" \
                   +urllib.quote("You have successfully registered"))
        elif action == 'unregister':
            self.manager.removeMember(member)
            return response.redirect(self.referring_url+"?portal_status_message=" \
                   +urllib.quote("You have successfully unregistered"))
        else:
            return "error -- no form.button.Submit specified"
    
    def isRegistered(self):
        memberTool = getToolByName(self.context, 'portal_membership')
        isAnonymous = memberTool.isAnonymousUser()
        member = memberTool.getAuthenticatedMember()
        return (not isAnonymous) and member.getMemberId() in self.manager.attendees()
