from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.minaraad.browser.configlets import AbstractView
from Products.minaraad.browser.utils import buildAttendeeCSV
from Products.minaraad.interfaces import IAttendeeManager
from Products.statusmessages.interfaces import IStatusMessage
from zope.cachedescriptors.property import Lazy
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.interface import Interface
from ZTUtils import make_query

import json
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
            message = ''
            if self.check_email(self.request.get('email')):
                attendee = self.attendee
            else:
                attendee = None
                message = 'E-mailadres is niet geldig.'
            query = ''
            if not attendee:
                if not message:
                    message = ('Alle velden zijn verplicht.')
                status = 'error'
                # Redirect including current form variables.
                new_form = {}
                for field in ('firstname', 'lastname', 'email', 'work'):
                    if field in self.request:
                        new_form[field] = self.request.get(field)
                query = make_query(new_form)
            else:
                self.manager.add_attendee(attendee)
                if self.request.form.get('remember'):
                    attendee.set_cookie(self.request)
                else:
                    attendee.unset_cookie(self.request)
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
            url = self.referring_url
            if query:
                url += '?' + query
            return response.redirect(url)
        elif action == 'unregister':
            attendee = self.attendee
            if not attendee:
                # This cannot really happen currently, as we get this from the
                # cookie.
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
        # Note: on GET requests this only returns info for authenticated users.
        # For anonymous users, all is done client side in javascript.
        if self.manager is None:
            return
        return self.manager.get_attendee(self.request)

    @security.protected(ManagePortal)
    def attendees(self):
        if self.manager is None:
            return []
        return self.manager.attendees()

    @Lazy
    def js_attendees(self):
        if self.manager is None:
            attendees = []
        else:
            attendees = self.manager.attendees()
        # Let json worry about correctly formatting and quoting this list.
        javascript_list = json.dumps(
            [attendee.hexdigest for attendee in attendees])
        return "event_attendees = {}".format(javascript_list)

    @security.protected(ManagePortal)
    def buildAttendeesCSV(self):
        context = aq_inner(self.context)
        return buildAttendeeCSV(
            context,
            self.attendees(),
            filename='%s-attendees.csv' % self.context.getId())

    def check_email(self, value):
        reg_tool = getToolByName(self, 'portal_registration')
        if value and reg_tool.isValidEmail(value):
            return True
        return False


class SimpleAttendeesView(AttendeesManagerView):

    def __call__(self):
        logger.debug('%s', self.context)
        return self.isRegistered()
