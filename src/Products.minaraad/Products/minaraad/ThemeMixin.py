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
from Acquisition import aq_chain
from Acquisition import aq_inner
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from Products.minaraad.content.interfaces import IThemes
from Products.minaraad.content.Theme import Theme
from zope.component import getUtility
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory

import logging


logger = logging.getLogger('minaraad')


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


theme_reference_schema = atapi.Schema((
    atapi.StringField(
        name='theme_path',
        widget=atapi.SelectionWidget(
            label='Theme',
            label_msgid='minaraad_label_theme',
            i18n_domain='minaraad',
        ),
        vocabulary_factory='minaraad.theme_path'
    ),

))


class ThemeReferenceMixin(object):
    implements(IThemes)

    security = ClassSecurityInfo()

    @security.public
    def getThemeTitle(self):
        """Get the theme name when it is set."""
        theme_path = self.getTheme_path()
        if theme_path:
            voc = getUtility(IVocabularyFactory, 'minaraad.theme_path')
            terms = voc(self)
            # Note: when a theme is private, it will not be in the vocabulary
            # for anonymous users or digibib users that are not authorized to
            # view the theme.  They will get a LookupError, which we catch.
            try:
                return terms.getTerm(theme_path).title
            except LookupError:
                pass
        # Theme path is not yet set or the theme object has been deleted since.
        # We use the one saved previously while saving the object.  This may
        # have been done by us or by the old theme mixin, but that is fine.
        try:
            return self._theme_name
        except AttributeError:
            return

    @security.private
    def setThemeTitle(self, theme_name):
        self._theme_name = theme_name

    @security.private
    def getThemeObject(self):
        """Get the theme object when it is set."""
        theme_path = self.getTheme_path()
        if not theme_path:
            return
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is None:
            return
        brains = catalog(
            portal_type='Theme',
            path={'query': theme_path, 'depth': 0})
        if len(brains) != 1:
            logger.warn('%d themes found at path %r, ignoring.',
                        len(brains), theme_path)
            return
        return brains[0].getObject()
