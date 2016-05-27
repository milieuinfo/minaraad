# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone import api
from Products.Five.browser import BrowserView
from Products.minaraad.utils import list_viewable
from zope.cachedescriptors.property import Lazy

import logging


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
        future = (now + 365).latestTime()
        brains = api.content.find(
            sort_order='ascending',
            sort_on='getStart_time',
            portal_type='MREvent',
            review_state='published',
            getStart_time={
                'query': (
                    now,
                    future,
                ),
                'range': 'min:max',
            },
        )
        return [brain.getObject() for brain in brains]

    def get_related(self):
        return list_viewable(self.context.getRelatedItems())
