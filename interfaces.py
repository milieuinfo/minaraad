from zope.interface import Interface, Attribute

class IPortalPropertyContainer(Interface):
    pass

class IAttendeeManager(Interface):
    
    def addAttendee(member):
        pass
    
    def removeAttendee(member):
        pass
    
    def attendees():
        pass

