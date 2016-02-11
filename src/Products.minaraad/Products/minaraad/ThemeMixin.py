# -*- coding: utf-8 -*-
"""
These are old style and new style themes.

The old style can be dropped after the 2016 upgrade.  Maybe even
before.  This comment claims that this logic is needed by an upgrade
step, but I [maurits] doubt it.

New theme logic is handled by putting a theme in a theme container
(new content type).  Thenew content type is defined here:

    `Products.minaraad/Products/minaraad/content/Theme.py`

The new way for objects to lookup their theme is the ThemeMixin:

    `Products.minaraad/Products/minaraad/ThemeMixin.py`

There will be three mixins in here:

- ThemeParentMixin, for object that have a new-style Theme in their path.

- ThemeReferenceMixin, for Digibib projects that reference a theme.

- OldThemeMixin, for objects using the old themes that were defined in
  properties in a control panel, using the ThemeManager.  Only for
  migration.

"""
from AccessControl import ClassSecurityInfo
from Acquisition import aq_chain, aq_inner
from Products.Archetypes import atapi
from Products.minaraad.content.Theme import Theme
from Products.minaraad.content.interfaces import IThemes
from Products.minaraad.themes import ThemeManager
from zope.interface import implements


class ThemeParentMixin(object):
    """Theme mixin for objects that have a Theme as parent in their path.

    It does not need to be a direct parent.
    """
    security = ClassSecurityInfo()

    @security.protected('View')
    def getThemeObject(self):
        """Get theme object.

        Look up the Theme for this object by traversing up to the first
        theme folder.

        :return: Theme or None
        """
        for obj in aq_chain(aq_inner(self)):
            if isinstance(obj, Theme):
                return obj

    @security.protected('View')
    def getThemeTitle(self):
        """Get title of theme object.

        :return: Theme title or empty string
        """
        theme = self.getThemeObject()
        if theme is None:
            return u''
        return theme.Title()


old_theme_schema = atapi.Schema((
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


class OldThemeMixin(object):
    implements(IThemes)

    security = ClassSecurityInfo()

    @security.public
    def getThemesList(self):
        """Get themes from minaraad properties."""
        themeManager = ThemeManager(self)
        return atapi.IntDisplayList(tuple(themeManager.themes))

    @security.public
    def getEmailThemesList(self):
        """ We can not use the same vocabulary as the values
        are stored as string and getThemesList returns a dictionnary
        with integer as keys.
        """
        themeManager = ThemeManager(self)
        return atapi.DisplayList(
            tuple([(str(thId), thName)
                   for thId, thName in themeManager.themes]))

    # getTheme is provided as archetype's default accessor if you use
    # old_theme_schema.
    @security.public
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
                  if id == themeId]

        if len(titles) != 1:
            # This theme might have been deleted since, we use the one
            # saved previously while saving the object.
            try:
                return self._theme_name
            except AttributeError:
                return

        return titles[0]

    @security.private
    def setThemeName(self, theme_name):
        self._theme_name = theme_name

    @security.private
    def get_all_themes(self):
        theme = self.getTheme()
        if theme is None:
            return self.getEmail_themes()

        return list(self.getEmail_themes()) + [str(theme)]
