from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from zope.interface import implements

from Products.minaraad.content.interfaces import IThemes
from Products.minaraad.themes import ThemeManager


theme_schema = atapi.Schema((
    atapi.IntegerField(
        name='theme',
        widget=atapi.SelectionWidget(
            label='Theme',
            label_msgid='minaraad_label_theme',
            i18n_domain='minaraad',
        ),
        vocabulary='getThemesList'
    ),

    atapi.LinesField(
        name='email_themes',
        widget=atapi.MultiSelectionWidget(
            label='Also send to subscribers of the following themes',
            label_msgid='minaraad_label_email_theme',
            i18n_domain='minaraad',
        ),
        vocabulary='getEmailThemesList',
        schemata='metadata'
    ),

    ))


class ThemeMixin(object):
    implements(IThemes)

    security = ClassSecurityInfo()

    security.declarePublic('getThemesList')
    def getThemesList(self):
        """Get themes from minaraad properties."""
        themeManager = ThemeManager(self)
        return atapi.IntDisplayList(tuple(themeManager.themes))

    security.declarePublic('getEmailThemesList')
    def getEmailThemesList(self):
        """ We can not use the same vocabulary as the values
        are stored as string and getThemesList returns a dictionnary
        with integer as keys.
        """
        themeManager = ThemeManager(self)
        return atapi.DisplayList(
            tuple([(str(thId), thName) for thId, thName in themeManager.themes]))

    # getTheme is provided as archetype's default accessor if you use
    # theme_schema.
    security.declarePublic('getThemeName')
    def getThemeName(self):
        """Get the theme name when it is set."""
        themeId = self.getTheme()
        if themeId is None:
            # Theme is not yet set (can happen for study/advisory as they only
            # got the theme field afterwards.
            return
        themeManager = ThemeManager(self)
        themeId = int(themeId)
        titles = [title for (id, title) in themeManager.themes
                  if id==themeId]

        if len(titles) != 1:
            # This theme might have been deleted since, we use the one
            # saved previously while saving the object.
            try:
                return self._theme_name
            except AttributeError:
                return

        return titles[0]

    def setThemeName(self, theme_name):
        self._theme_name = theme_name

    def get_all_themes(self):
        theme = self.getTheme()
        if theme is None:
            return self.getEmail_themes()

        return list(self.getEmail_themes()) + [str(theme)]
