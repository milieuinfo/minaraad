from zope.interface import Interface


class IDigiBib(Interface):
    """ Interface for the DigiBib content type.
    """

    def list_projects():
        """ Provides the list of projects
        """

    def list_meetings():
        """ Provides the list of meetings
        """


class IProject(Interface):
    """ Interface for the Project content type.
    """


class IBaseMeeting(Interface):
    """ Interface for the the base meetings
    (also include meetings in Products.minaraad)
    """


class IMeeting(Interface):
    """ Interface for the Meeting content type.
    """


class IAgendaItem(Interface):
    """ Interface for Agenda items.
    """


class IAgendaItemProject(Interface):
    """ This one is only for AgendaItem content
    type defined in this package.
    """


class IAttachment(Interface):
    """ Marker interface for attachment.
    """


class IOrganisation(Interface):
    """ Marker interface for organisations.
    """


class IProjectContainer(Interface):
    """ Marker interface for ProjectContainer.
    """


class IMeetingContainer(Interface):
    """ Marker interface for MeetingContainer.
    """


class IOrganisationContainer(Interface):
    """ Marker interface for OrganisationContainer.
    """


class IPASMemberView(Interface):
    # Taken from PlonePAS in Plone 4.0

    def info(self, userid=None):
        """Return 'harmless' member info of any user, such as full name,
        location, etc.
        """
