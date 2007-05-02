import urllib
from zope.interface import Interface, implements
from configlets import AbstractView
from Products.CMFCore.utils import getToolByName
from Products.minaraad.interfaces import IAttendeeManager
from Products.CMFCore.permissions import ManagePortal
from AccessControl import ClassSecurityInfo
from Products.minaraad.browser.utils import buildCSV
from zope.component import getMultiAdapter

class IAttendeesManagerView(Interface):

    def isRegistered():
        pass

    def groupedAttendees(self):
        pass

class AttendeesManagerView(AbstractView):
    implements(IAttendeesManagerView)

    security = ClassSecurityInfo()
    
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

        action = self.request.get('form.submitted', None)
        memberId = memberTool.getAuthenticatedMember().getId()
        if action == 'register':
            self.manager.addMember(memberId)
            if self.notifyRegistration(memberId, True):
                message =  'You have successfully registered, but sending email notification failed.'
            else:
                message = 'You have succesfully registered. U ontvangt hiervan nog een bevestiging per e-mail.'
            return response.redirect(self.referring_url+"?portal_status_message=" + urllib.quote(message))
        elif action == 'unregister':
            self.manager.removeMember(memberId)
            self.notifyRegistration(memberId, False)
            if self.notifyRegistration(memberId, True):
                message =  'You have successfully un registered, but sending email notification failed.'
            else:
                message = 'You have succesfully unregistered. U ontvangt hiervan nog een bevestiging per e-mail.'
            return response.redirect(self.referring_url+"?portal_status_message=" + urllib.quote(message))
        elif action == 'exportCSV':
            return self.buildAttendeesCSV()
        
        else:
            return "error -- no form.button.Submit specified"
    
    def notifyRegistration(self, memberId, subscribe):
        memberTool = getToolByName(self.context, 'portal_membership')
        member = memberTool.getMemberById(memberId)
        emailview = getMultiAdapter((self.context, self.request), name='notify_registration')
        failed_postings = emailview(member, subscribe)

    def isRegistered(self):
        memberTool = getToolByName(self.context, 'portal_membership')
        isAnonymous = memberTool.isAnonymousUser()
        member = memberTool.getAuthenticatedMember()
        return (not isAnonymous) and member.getMemberId() in self.manager.attendees()
    
    security.declareProtected(ManagePortal,'groupedAttendees')
    def groupedAttendees(self):
        attendees = {'council_members': [],
                     'members': []}
                     
        memTool = getToolByName(self.context, 'portal_membership')
        
        for memberId in self.manager.attendees():
            member = memTool.getMemberById(memberId)

            # In case a memberId is None (this happens when a user is deleted)
            # we remove the member as attendee on this hearing.
            #
            # Note: this means we will change history in case the member has
            # participated in a hearing. But that's the way they want it. 
            if member is None:
                self.manager.removeMember(memberId)
                continue

            nice = member.getProperty('firstname', '') + ' ' + \
                   member.getProperty('fullname', '')
            nice = nice.strip()
            if not nice:
                nice = memberId
            
            roles = member.getRolesInContext(self.context)
            if 'Council Member' in roles:
                group = attendees['council_members']
            else:
                group = attendees['members']
            
            group.append({'memberId': memberId,
                          'niceName': nice})
        
        return attendees

    security.declareProtected(ManagePortal, 'buildAttendeesCSV')
    def buildAttendeesCSV(self):
        memTool = getToolByName(self.context, 'portal_membership')
        attendees = [memTool.getMemberById(memid)
                     for memid in self.manager.attendees()]

        ploneUtils = getToolByName(self.context, 'plone_utils')
        
        return buildCSV(self.context,
                        attendees,
                        filename='%s-attendees.csv' % self.context.getId())
