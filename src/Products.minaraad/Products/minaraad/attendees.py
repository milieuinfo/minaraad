from hashlib import md5
from persistent import Persistent
from persistent.list import PersistentList
from Products.minaraad.interfaces import IAttendeeManager
from zope.event import notify
from zope.interface import implements
from zope.lifecycleevent import ObjectModifiedEvent


COOKIE_ID = 'minaraad_attendee'


class Attendee(Persistent):
    # XXX Maybe just object instead of Persistent.

    def __init__(self, fullname='', email='', work=''):
        self.fullname = fullname
        self.email = email
        self.work = work
        self.id = None

    def from_member(self, member):
        self.fullname = member.getProperty('fullname')
        self.email = member.getProperty('email')
        work_parts = [
            member.getProperty('jobtitle', '').strip(),
            member.getProperty('company').strip()]
        self.work = ' / '.join([p for p in work_parts if p])

    def from_form(self, request):
        form = self.request.form
        self.fullname = form.get('fullname', '')
        self.email = form.get('email', '')
        self.work = form.get('work', '')

    def from_cookie(self, request):
        cookie = self.request.cookies.get(COOKIE_ID, '')
        if not cookie:
            return
        parts = cookie.split('#')
        if len(parts) != 3:
            return
        self.fullname, self.email, self.work = parts

    def set_cookie(self, request):
        request.cookies.set(COOKIE_ID, self.hash_base)

    @property
    def hash_base(self):
        return '#'.join([self.fullname, self.email, self.work])

    def calc_uid(self):
        return md5(self.hash_base).hexdigest()


class AttendeeManager(object):
    implements(IAttendeeManager)

    def __init__(self, context):
        self.context = context

    def update(self):
        # Update the modification date, so some caches can be purged
        # or etags outdated.
        self.context.setModificationDate()
        self.context.reindexObject()
        notify(ObjectModifiedEvent(self.context))

    def add_attendee(self, attendee):
        attendees = self.attendees()
        next_number = getattr(
            self.context, '_next_attendee_number', len(attendees))
        attendee.id = next_number
        attendees.append(attendee)
        self.context._attendees = attendees
        self.context._next_attendee_number = next_number + 1
        self.update()

    def remove_attendee(self, memberId):
        attendees = self.attendees()
        try:
            attendees.remove(memberId)
        except ValueError:
            # this is ok
            pass

        self.context._attendees = attendees
        self.update()

    def attendees(self):
        return getattr(self.context, '_attendees', PersistentList())
