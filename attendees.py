from zope.interface import implements, Interface
from Products.minaraad.interfaces import IAttendeeManager

class AttendeeManager(object):
    implements(IAttendeeManager)

    def __init__(self, context):
        self.context = context
        
    def addMember(self, member):
        attendees = self.attendees()
        
        memberId = member
        if not isinstance(member, basestring):
            memberId = member.getMemberId()
            
        attendees.append(memberId)
        
        self.context._attendees = attendees
    
    def removeMember(self, member):
        attendees = self.attendees()

        memberId = member
        if not isinstance(member, basestring):
            memberId = member.getMemberId()

        self.context._attendees = attendees
        
    def attendees(self):
        return getattr(self.context, '_attendees', [])
