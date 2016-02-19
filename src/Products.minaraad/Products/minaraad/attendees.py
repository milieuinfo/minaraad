from Acquisition import aq_inner
from email.utils import formatdate
from persistent import Persistent
from persistent.list import PersistentList
from Products.CMFCore.utils import getToolByName
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
        self.cleanup()

    def is_blank(self):
        return not (self.email and self.lastname)

    @property
    def name(self):
        # For the mail we prefer the first name, but it is not required.
        return self.firstname or self.lastname

    def from_member(self, member):
        self.firstname = member.getProperty('firstname', '')
        # Note: in this site, the fullname property of a member contains only
        # the last name.
        self.lastname = member.getProperty('fullname', '')
        self.email = member.getProperty('email', '')
        work_parts = [
            member.getProperty('jobtitle', '').strip(),
            member.getProperty('company', '').strip()]
        self.work = ' / '.join([p for p in work_parts if p])
        self.cleanup()

    def from_form(self, request):
        form = request.form
        self.firstname = form.get('firstname', '')
        self.lastname = form.get('lastname', '')
        self.email = form.get('email', '')
        self.work = form.get('work', '')
        self.cleanup()

    def from_cookie(self, request):
        cookie = request.cookies.get(COOKIE_ID, '')
        if not cookie:
            return
        parts = cookie.split('#')
        if len(parts) != 4:
            return
        self.firstname, self.lastname, self.email, self.work = parts
        self.cleanup()

    def set_cookie(self, request):
        # Expire in two years
        expires = time.time() + (2 * 365 * 24 * 60 * 60)
        expires = formatdate(expires, usegmt=True)
        request.response.setCookie(
            COOKIE_ID, self.hash_base, path='/', expires=expires)

    def cleanup(self):
        # Remove trailing spaces, and remove hashes because they interfere with
        # how we create and read the cookie.
        for prop in ('email', 'lastname', 'firstname', 'work'):
            value = getattr(self, prop, '')
            new_value = value.strip().replace('#', ' ')
            setattr(self, prop, new_value)

    @property
    def hash_base(self):
        # Calling cleanup should be superfluous, but let's be sure.
        self.cleanup()
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

    def get_attendee(self, request):
        # Get an attendee object for the visitor.
        # First check the submitted form, if any.
        attendee = self.get_from_form(request)
        if attendee is not None:
            return attendee
        # Then check the cookie, if any.
        attendee = self.get_from_cookie(request)
        if attendee is not None:
            return attendee
        # Then check the authenticated member, if any.
        context = aq_inner(self.context)
        memberTool = getToolByName(context, 'portal_membership')
        if memberTool.isAnonymousUser():
            return
        member = memberTool.getAuthenticatedMember()
        attendee = self.get_from_member(member)
        if attendee is not None:
            return attendee

    def update(self):
        # Update the modification date, so some caches can be purged
        # or etags outdated.
        self.context.setModificationDate()
        self.context.reindexObject()
        notify(ObjectModifiedEvent(self.context))

    def add_attendee(self, attendee):
        attendees = self.attendees()
        if attendee in attendees:
            return
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
