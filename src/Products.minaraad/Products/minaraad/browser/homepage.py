# -*- coding: utf-8 -*-
import logging
from DateTime import DateTime
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.cachedescriptors.property import Lazy
from zope.component import getMultiAdapter
from plone import api

logger = logging.getLogger('Products.minaraad')

# def getSitePath(context, request):
#     portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
#     site = portal_state.portal()
#     site_path = site.getPhysicalPath()
#     return "/".join(site_path)


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

        # Catalog
        # catalog = getToolByName(self.context, 'portal_catalog')
        # brains = catalog.searchResults(
        #
        #         sort_order='ascending',
        #         portal_type="MREvent",
        #         getStart_time={
        #             'query': (
        #                 now,
        #                 future,
        #             ),
        #             'range': 'min:max',
        #         }
        # )
        return brains




    # def related_items(self):
    #
    #     items = []
    #     for item in self.context.getRelatedItems():
    #         dp_helper = getMultiAdapter(
    #                 (item, self.request),
    #                 name='default_page'
    #         )
    #         items.append(dp_helper.getDefaultPage(item))
    #
    #     import pdb; pdb.set_trace()
    #     return items


    # def slides(self):
    #     site_path = getSitePath(self.context, self.request)
    #     query_path = site_path + '/slides'
    #     objects = self.catalog({
    #         'portal_type': 'Image',
    #         'path': {'query': query_path, 'depth': 1},
    #     })
    #     return [obj.getObject() for obj in objects]
    #
    # def logos(self):
    #     objects = self.catalog(portal_type='zest.content.case')
    #     objects = [obj.getObject() for obj in objects]
    #     logos = carousel_slide_distribution([obj for obj in objects if obj.logo_on_home is True])
    #     return logos
    #
    # def quotes(self):
    #     objects = self.catalog(portal_type='zest.content.quote')
    #     return [obj.getObject() for obj in objects]
