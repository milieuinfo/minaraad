from plone.app.layout.viewlets import common as base
from zope.cachedescriptors.property import Lazy
from plone import api

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
