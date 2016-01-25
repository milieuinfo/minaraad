# -*- coding: utf-8 -*-
import logging
from DateTime import DateTime
from Products.Five.browser import BrowserView
from zope.cachedescriptors.property import Lazy
from plone import api

logger = logging.getLogger('Products.minaraad')


class HomepageView(BrowserView):
    """
    Homepage View.
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

    def future_events(self):
        now = DateTime().earliestTime()
        future = DateTime(now.year() + 1, now.month(), now.day()).latestTime()
        brains = api.content.find(
            sort_order='ascending',
            portal_type="MREvent",
            getStart_time={
                'query': (
                    now,
                    future,
                ),
                'range': 'min:max',
            },

        )
        return brains
