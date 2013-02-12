from zope.component.hooks import getSite
from OFS.interfaces import IFolder

from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets.common import GlobalSectionsViewlet

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class MinaGlobalSectionsViewlet(GlobalSectionsViewlet):
    index = ViewPageTemplateFile('sections.pt')

    def get_hidden_titles(self):
        portal = getSite()
        portal_props = getToolByName(portal, 'portal_properties')
        return portal_props.navtree_properties.titlesNotInTabs

    def get_sitemap(self):
        portal = getSite()
        return self.context.plone_utils.createSitemap(portal)
