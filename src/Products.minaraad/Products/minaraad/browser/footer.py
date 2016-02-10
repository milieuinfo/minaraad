from plone.app.layout.viewlets import common as base
from zope.cachedescriptors.property import Lazy
from plone import api
from zope.component import getMultiAdapter

class MinaFooter(base.ViewletBase):
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
        return [brain.getObject() for brain in brains][:6]

    def menu_items(self):
        # Get CatalogNavigationTabs instance
        portal_tabs_view = getMultiAdapter((self.context, self.request),
                                       name='portal_tabs_view')

        # Action parameter is "portal_tabs" by default, but can be other
        portal_tabs = portal_tabs_view.topLevelTabs(actions=None)
        return portal_tabs
