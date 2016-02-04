# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from plone import api
from Products.minaraad.content.Theme import Theme


class ThemeMixin(object):
    """ ThemeMixin
    """
    security = ClassSecurityInfo()

    def getThemeObject(self):
        """Get theme object.

        Look up the Theme for this object by traversing up to the first
        theme folder.

        :return: Theme or None
        """
        portal = api.portal.get()
        obj = self.aq_parent
        while not isinstance(obj, Theme):
            if obj == portal:
                return None
            obj = self.aq_parent
        return obj

    def getThemeTitle(self):
        """Get title of theme object.

        :return: Theme title or empty string
        """
        theme = self.getThemeObject()
        if theme is None:
            return u''
        return theme.Title()
