# -*- coding: utf-8 -*-
from plone import api
from Products.Five.browser import BrowserView
from Products.minaraad.utils import list_viewable
from zope.cachedescriptors.property import Lazy

import logging


logger = logging.getLogger('Products.minaraad')


class ThemeListView(BrowserView):
    """
    Theme List View.
    """

    def __call__(self):
        return self.index()

    @Lazy
    def portal(self):
        return api.portal.get()

    def themes(self):
        brains = api.content.find(
            context=self.portal,
            portal_type="Theme",
        )
        return [brain.getObject() for brain in brains]

    def primary_themes(self):
        if len(self.themes()) >= 6:
            return self.themes()[:6]

    def secondary_themes(self):
        if len(self.themes()) > 6:
            return self.themes()[6:]


class ThemeView(ThemeListView):
    """
    Theme View.
    """

    def get_related(self):
        return list_viewable(self.context.getRelatedItems())
