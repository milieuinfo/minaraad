import logging
import urllib

from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter
from zope.interface import Interface, implements

from Products.minaraad.browser.configlets import AbstractView
from Products.minaraad.browser.utils import buildCSV
from Products.minaraad.interfaces import IAttendeeManager

logger = logging.getLogger('minaraad')


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
        self.manager = IAttendeeManager(args[0], None)

    def __call__(self):
        context = aq_inner(self.context)
        memberTool = getToolByName(context, 'portal_membership')
        isAnonymous = memberTool.isAnonymousUser()
        portal = getToolByName(context, 'portal_url').getPortalObject()
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
                # notifyRegistration returns list of failed email addresses,
                # so a match means that there's some error.
                message = 'Uw inschrijving is gelukt, maar het verzenden van de bevestigingse-mail is niet gelukt.'
                status = 'warning'
            else:
                message = 'Uw inschrijving is gelukt. U ontvangt hiervan nog een bevestiging per e-mail.'
                status = 'info'
            IStatusMessage(self.request).addStatusMessage(message, type=status)
            return response.redirect(self.referring_url + '?submitted=1')
        elif action == 'unregister':
            self.manager.removeMember(memberId)
            if self.notifyRegistration(memberId, False):
                message = 'Het afmelden is gelukt, maar het verzenden van de bevestigingse-mail is niet gelukt.'
                status = 'warning'
            else:
                message = 'Het afmelden is gelukt. U ontvangt hiervan nog een bevestiging per e-mail.'
                status= 'info'
            IStatusMessage(self.request).addStatusMessage(message, type=status)
            return response.redirect(self.referring_url + '?submitted=1')
        elif action == 'exportCSV':
            return self.buildAttendeesCSV()

        else:
            return "error -- no form.button.Submit specified"

    def notifyRegistration(self, memberId, subscribe):
        context = aq_inner(self.context)
        memberTool = getToolByName(context, 'portal_membership')
        member = memberTool.getMemberById(memberId)
        emailview = getMultiAdapter((context, self.request),
                                    name='notify_registration')
        failed_postings = emailview(member, subscribe)
        return failed_postings

    def isRegistered(self):
        if self.manager is None:
            return False
        context = aq_inner(self.context)
        memberTool = getToolByName(context, 'portal_membership')
        if memberTool.isAnonymousUser():
            return False
        member = memberTool.getAuthenticatedMember()
        return member.getMemberId() in self.manager.attendees()

    security.declareProtected(ManagePortal, 'groupedAttendees')
    def groupedAttendees(self):
        context = aq_inner(self.context)
        attendees = {'council_members': [],
                     'members': []}

        memTool = getToolByName(context, 'portal_membership')
        for memberId in self.manager.attendees():
            logger.debug('%s is attending', memberId)
            member = memTool.getMemberById(memberId)

            # In case a memberId is None (this happens when a user is deleted)
            # we remove the member as attendee on this hearing.
            #
            # Note: this means we will change history in case the member has
            # participated in a hearing. But that's the way they want it.
            if member is None:
                logger.info("Removing non-member %s from attendees of %s",
                            memberId, context.absolute_url())
                self.manager.removeMember(memberId)
                continue

            nice = member.getProperty('firstname', '') + ' ' + \
                   member.getProperty('fullname', '')
            nice = nice.strip()
            if not nice:
                nice = memberId

            roles = member.getRolesInContext(context)
            if 'Council Member' in roles:
                group = attendees['council_members']
            else:
                group = attendees['members']

            group.append({'memberId': memberId,
                          'niceName': nice})

        return attendees

    security.declareProtected(ManagePortal, 'buildAttendeesCSV')
    def buildAttendeesCSV(self):
        context = aq_inner(self.context)
        memTool = getToolByName(context, 'portal_membership')
        attendees = [memTool.getMemberById(memid)
                     for memid in self.manager.attendees()]
        return buildCSV(context,
                        attendees,
                        filename='%s-attendees.csv' % self.context.getId())


class SimpleAttendeesView(AttendeesManagerView):

    def __call__(self):
        logger.debug('%s', self.context)
        return self.isRegistered()
