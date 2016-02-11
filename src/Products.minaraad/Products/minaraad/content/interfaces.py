from zope.interface import Interface


class IThemes(Interface):
    """Lists applicable themes and provides theme displaylist.

    This was used by the OldThemeMixin (with a few more methods) and
    will from now on be used by the ThemeReferenceMixin.
    """

    def getThemeName():
        """Return name of selected theme"""


class IUseContact(Interface):
    """ Marker interface for objects using contacts.
    """
