from zope.interface import Interface


class IThemes(Interface):
    """Lists applicable themes and provides theme displaylist."""

    def getThemesList():
        """Return displaylist with theme id/name"""

    def getTheme():
        """Return ID of selected theme"""

    def getThemeName():
        """Return name of selected theme"""


class IUseContact(Interface):
    """ Marker interface for objects using contacts.
    """
