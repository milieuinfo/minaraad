from email.utils import formatdate
from persistent import Persistent
from persistent.list import PersistentList
from Products.minaraad.interfaces import IAttendeeManager
from zope.event import notify
from zope.interface import implements
from zope.lifecycleevent import ObjectModifiedEvent

import time


COOKIE_ID = 'minaraad_attendee'


class Attendee(Persistent):

    def __init__(self, firstname='', lastname='', email='', work=''):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.work = work

    def is_blank(self):
        return not (self.email and self.lastname)

    def from_member(self, member):
        self.firstname = member.getProperty('firstname')
        self.lastname = member.getProperty('lastname')
        self.email = member.getProperty('email')
        work_parts = [
            member.getProperty('jobtitle', '').strip(),
            member.getProperty('company').strip()]
        self.work = ' / '.join([p for p in work_parts if p])

    def from_form(self, request):
        form = request.form
        self.firstname = form.get('firstname', '')
        self.lastname = form.get('lastname', '')
        self.email = form.get('email', '')
        self.work = form.get('work', '')

    def from_cookie(self, request):
        cookie = request.cookies.get(COOKIE_ID, '')
        if not cookie:
            return
        parts = cookie.split('#')
        if len(parts) != 4:
            return
        self.firstname, self.lastname, self.email, self.work = parts

    def set_cookie(self, request):
        # Expire in two years
        expires = time.time() + (2 * 365 * 24 * 60 * 60)
        expires = formatdate(expires, usegmt=True)
        request.response.setCookie(
            COOKIE_ID, self.hash_base, path='/', expires=expires)

    @property
    def hash_base(self):
        return '#'.join([self.firstname, self.lastname, self.email, self.work])

    def __repr__(self):
        return '<Products.minaraad.attendees.Attendee object {} {}>'.format(
            self.firstname, self.lastname)

    def __str__(self):
        return '{} {}'.format(self.firstname, self.lastname)

    def __eq__(self, other):
        # The == operator.  Used when checking if an attendee is in the list of
        # attendees.
        for prop in ('email', 'lastname', 'firstname', 'work'):
            if getattr(self, prop, '') != getattr(other, prop, ''):
                return False
        return True

    def __ne__(self, other):
        # The != operator.
        return not self.__eq__(other)


class AttendeeManager(object):
    implements(IAttendeeManager)

    def __init__(self, context):
        self.context = context

    def get_from_cookie(self, request):
        attendee = Attendee()
        attendee.from_cookie(request)
        if not attendee.is_blank():
            return attendee

    def get_from_form(self, request):
        attendee = Attendee()
        attendee.from_form(request)
        if not attendee.is_blank():
            return attendee

    def get_from_member(self, member):
        attendee = Attendee()
        attendee.from_member(member)
        if not attendee.is_blank():
            return attendee

    def add_from_form(self, request):
        # Add an attendee based on a form.
        # Return the attendee object.
        attendee = Attendee()
        attendee.from_form(request)
        if attendee.is_blank():
            return
        self.add_attendee(attendee)
        if request.form.get('remember'):
            attendee.set_cookie(request)
        return attendee

    def remove_from_form(self, request):
        # Remove an attendee based on a form.
        # Return the attendee object.
        attendee = Attendee()
        attendee.from_form(request)
        if attendee.is_blank():
            return
        self.remove_attendee(attendee)
        return attendee

    def update(self):
        # Update the modification date, so some caches can be purged
        # or etags outdated.
        self.context.setModificationDate()
        self.context.reindexObject()
        notify(ObjectModifiedEvent(self.context))

    def add_attendee(self, attendee):
        attendees = self.attendees()
        attendees.append(attendee)
        # Yes, it is a persistent list, but it might not have been saved on the
        # context yet.  So we simply always save it explicitly.
        self.context._attendees = attendees
        self.update()

    def is_attendee(self, attendee):
        return attendee in self.attendees()

    def remove_attendee(self, attendee):
        attendees = self.attendees()
        try:
            attendees.remove(attendee)
        except ValueError:
            # this is ok
            pass
        self.update()

    def attendees(self):
        return getattr(self.context, '_attendees', PersistentList())
