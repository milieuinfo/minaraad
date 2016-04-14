from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase, GlobalSectionsViewlet
from zope.component import getMultiAdapter


class MinaGlobalSectionsViewlet(GlobalSectionsViewlet):
    index = ViewPageTemplateFile('sections.pt')

    def _get_portal(self):
        # Just a little helper function.  We used getSite() from
        # zope.component.hooks first, but that returned a
        # ValidationView when doing inline validation.
        context = aq_inner(self.context)
        pps = getMultiAdapter((context, self.request),
                              name='plone_portal_state')
        return pps.portal()

    def get_hidden_titles(self):
        portal = self._get_portal()
        portal_props = getToolByName(portal, 'portal_properties')
        if not portal_props.navtree_properties.hasProperty('titlesNotInTabs'):
            return []
        return portal_props.navtree_properties.titlesNotInTabs

    def get_sitemap(self):
        portal = self._get_portal()
        plone_utils = getToolByName(portal, 'plone_utils')
        return plone_utils.createSitemap(portal)


class RelatedDocumentsViewlet(ViewletBase):
    """docstring for RelatedDocumentsViewlet(ViewletBase)"""
    index = ViewPageTemplateFile('related_documents.pt')

    def title(self):
        context = aq_inner(self.context)
        if context.portal_type in ("Advisory", "MREvent", "Study"):
            return u"Gerelateerde documenten"
        else:
            return u"Actuele documenten"

    def get_related_documents(self):
        context = aq_inner(self.context)
        if context.portal_type in ("Advisory", "MREvent", "Study"):
            related_items = sorted(context.getRelatedDocuments(),
                key=lambda item: item.effective_date, reverse=True)
            return related_items
        elif context.getId() == 'thema-lijst':
            return context.getRelatedItems()
