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


class IAnnualReport(Interface):
    """ Marker interface for Annual reports.
    """


class IHearing(Interface):
    """ Marker interface for Hearing.
    """


class IMREvent(Interface):
    """ Marker interface for MREvent.
    """


class INewsItem(Interface):
    """ Marker interface for NewsItem.
    """


class INewsLetter(Interface):
    """ Marker interface for MREvent.
    """


class IStudy(Interface):
    """ Marker interface for Study.
    """


class IContactPerson(Interface):
    """ Marker interface for contact person.
    """
