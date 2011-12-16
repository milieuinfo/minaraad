from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.interface import implements
from Products.minaraad.interfaces import IAttendeeManager
from persistent.list import PersistentList


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

    def addMember(self, member):
        attendees = self.attendees()

        memberId = member
        if not isinstance(member, basestring):
            memberId = member.getMemberId()

        attendees.append(memberId)

        self.context._attendees = attendees
        self.update()

    def removeMember(self, memberId):
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
