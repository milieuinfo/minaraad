# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Acquisition import aq_chain, aq_inner
from Products.minaraad.content.Theme import Theme


class ThemeParentMixin(object):
    """Theme mixin for objects that have a Theme as parent in their path.

    It does not need to be a direct parent.
    """
    security = ClassSecurityInfo()

    def getThemeObject(self):
        """Get theme object.

        Look up the Theme for this object by traversing up to the first
        theme folder.

        :return: Theme or None
        """
        for obj in aq_chain(aq_inner(self)):
            if isinstance(obj, Theme):
                return obj

    def getThemeTitle(self):
        """Get title of theme object.

        :return: Theme title or empty string
        """
        theme = self.getThemeObject()
        if theme is None:
            return u''
        return theme.Title()
