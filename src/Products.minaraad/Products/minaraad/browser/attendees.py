from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Products.CMFCore.permissions import ManagePortal
from Products.minaraad.browser.configlets import AbstractView
from Products.minaraad.browser.utils import buildAttendeeCSV
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
        if self.request.get('REQUEST_METHOD', 'GET').upper() != 'POST':
            return 'ERROR: must be POST request.'
        response = self.request.response
        action = self.request.get('form.submitted', None)
        if action == 'register':
            attendee = self.attendee
            if not attendee:
                message = ('Achternaam en emailadres zijn verplicht.')
                status = 'error'
            else:
                self.manager.add_attendee(attendee)
                if self.request.form.get('remember'):
                    attendee.set_cookie(self.request)
                if self.notifyRegistration(attendee, True):
                    # notifyRegistration returns a list of failures, so a match
                    # means that there is some error.
                    message = ('Uw inschrijving is gelukt, maar het verzenden '
                               'van de bevestigingse-mail is niet gelukt.')
                    status = 'warning'
                else:
                    message = ('Uw inschrijving is gelukt. U ontvangt hiervan '
                               'nog een bevestiging per e-mail.')
                    status = 'info'
            # Note that adding a statusmessage cookie has the side effect of
            # preventing caching, which is good.
            IStatusMessage(self.request).addStatusMessage(message, type=status)
            return response.redirect(self.referring_url)
        elif action == 'unregister':
            attendee = self.attendee
            if not attendee:
                message = ('Achternaam en emailadres zijn verplicht.')
                status = 'error'
            else:
                self.manager.remove_attendee(attendee)
                if self.notifyRegistration(attendee, False):
                    message = ('Het afmelden is gelukt, maar het verzenden '
                               'van de bevestigingse-mail is niet gelukt.')
                    status = 'warning'
                else:
                    message = ('Het afmelden is gelukt. U ontvangt hiervan '
                               'nog een bevestiging per e-mail.')
                    status = 'info'
            IStatusMessage(self.request).addStatusMessage(message, type=status)
            return response.redirect(self.referring_url)
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
        return self.manager.get_attendee(self.request)

    @security.protected(ManagePortal)
    def attendees(self):
        if self.manager is None:
            return []
        return self.manager.attendees()

    @security.protected(ManagePortal)
    def buildAttendeesCSV(self):
        context = aq_inner(self.context)
        return buildAttendeeCSV(
            context,
            self.attendees(),
            filename='%s-attendees.csv' % self.context.getId())


class SimpleAttendeesView(AttendeesManagerView):

    def __call__(self):
        logger.debug('%s', self.context)
        return self.isRegistered()
