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
    # XXX Maybe just object instead of Persistent.

    def __init__(self, fullname='', email='', work=''):
        self.fullname = fullname
        self.email = email
        self.work = work
        # self.id = None

    def is_blank(self):
        return not (self.email and self.fullname)

    def from_member(self, member):
        self.fullname = member.getProperty('fullname')
        self.email = member.getProperty('email')
        work_parts = [
            member.getProperty('jobtitle', '').strip(),
            member.getProperty('company').strip()]
        self.work = ' / '.join([p for p in work_parts if p])

    def from_form(self, request):
        form = request.form
        self.fullname = form.get('fullname', '')
        self.email = form.get('email', '')
        self.work = form.get('work', '')

    def from_cookie(self, request):
        cookie = request.cookies.get(COOKIE_ID, '')
        if not cookie:
            return
        parts = cookie.split('#')
        if len(parts) != 3:
            return
        self.fullname, self.email, self.work = parts

    def set_cookie(self, request):
        # Expire in two years
        expires = time.time() + (2 * 365 * 24 * 60 * 60)
        expires = formatdate(expires, usegmt=True)
        request.response.setCookie(
            COOKIE_ID, self.hash_base, path='/', expires=expires)

    @property
    def hash_base(self):
        return '#'.join([self.fullname, self.email, self.work])

    # def calc_uid(self):
    #     from hashlib import md5
    #     return md5(self.hash_base).hexdigest()


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
