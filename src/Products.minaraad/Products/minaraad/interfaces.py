from zope.interface import Interface


class IPortalPropertyContainer(Interface):
    pass


class IAttendeeManager(Interface):

    def addAttendee(member):
        pass

    def removeAttendee(member):
        pass

    def attendees():
        pass

class IPressRelease(Interface):
    """ Marker interface for Press release.
    """

class IAdvisory(Interface):
    """ Marker interface for Advisory.
    """
