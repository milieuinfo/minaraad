from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.minaraad.browser.configlets import AbstractView
from Products.minaraad.browser.utils import buildCSV
from Products.minaraad.interfaces import IAttendeeManager
from Products.statusmessages.interfaces import IStatusMessage
from zope.cachedescriptors.property import Lazy
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.interface import Interface

import logging


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
        response = self.request.response
        action = self.request.get('form.submitted', None)
        if action == 'register':
            submitted = True
            attendee = self.manager.add_from_form(self.request)
            if not attendee:
                message = ('Volledige naam en emailadres zijn verplicht.')
                status = 'error'
                submitted = False
            elif self.notifyRegistration(attendee, True):
                # notifyRegistration returns a list of failures, so a match
                # means that there is some error.
                message = ('Uw inschrijving is gelukt, maar het verzenden '
                           'van de bevestigingse-mail is niet gelukt.')
                status = 'warning'
            else:
                message = ('Uw inschrijving is gelukt. U ontvangt hiervan '
                           'nog een bevestiging per e-mail.')
                status = 'info'
            IStatusMessage(self.request).addStatusMessage(message, type=status)
            url = self.referring_url
            if submitted:
                url += '?submitted=1'
            return response.redirect(url)
        elif action == 'unregister':
            submitted = True
            attendee = self.manager.remove_from_form(self.request)
            if not attendee:
                message = ('Volledige naam en emailadres zijn verplicht.')
                status = 'error'
                submitted = False
            elif self.notifyRegistration(attendee, False):
                message = ('Het afmelden is gelukt, maar het verzenden '
                           'van de bevestigingse-mail is niet gelukt.')
                status = 'warning'
            else:
                message = ('Het afmelden is gelukt. U ontvangt hiervan '
                           'nog een bevestiging per e-mail.')
                status = 'info'
            IStatusMessage(self.request).addStatusMessage(message, type=status)
            url = self.referring_url
            if submitted:
                url += '?submitted=1'
            return response.redirect(url)
        elif action == 'exportCSV':
            return self.buildAttendeesCSV()

        else:
            return "error -- no form.button.Submit specified"

    def notifyRegistration(self, attendee, subscribe):
        """Send a notification about registration.

        subscribe is True for subscribing, False for unsubscribing.
        """
        context = aq_inner(self.context)
        emailview = getMultiAdapter((context, self.request),
                                    name='notify_registration')
        failed_postings = emailview(attendee, subscribe)
        return failed_postings

    def isRegistered(self):
        if self.attendee is None:
            return False
        return self.manager.is_attendee(self.attendee)

    @Lazy
    def attendee(self):
        # Get an attendee object for the visitor.
        if self.manager is None:
            return
        # First check the submitted form, if any.
        attendee = self.manager.get_from_form(self.request)
        if attendee is not None:
            return attendee
        # Then check the cookie, if any.
        attendee = self.manager.get_from_cookie(self.request)
        if attendee is not None:
            return attendee
        # Then check the authenticated member, if any.
        context = aq_inner(self.context)
        memberTool = getToolByName(context, 'portal_membership')
        if memberTool.isAnonymousUser():
            return
        member = memberTool.getAuthenticatedMember()
        attendee = self.manager.get_from_member(member)
        if attendee is not None:
            return attendee

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
