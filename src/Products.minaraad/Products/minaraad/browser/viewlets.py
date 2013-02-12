from zope.component.hooks import getSite
from OFS.interfaces import IFolder

from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets.common import GlobalSectionsViewlet

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class MinaGlobalSectionsViewlet(GlobalSectionsViewlet):
    index = ViewPageTemplateFile('sections.pt')

    def get_portal_tabs(self):
        portal = getSite()
        tabs = self.portal_tabs

        portal_props = getToolByName(portal, 'portal_properties')
        hidden_titles = portal_props.navtree_properties.titlesNotInTabs

        for tab in tabs:
            tab_id = tab.get('id', None)
            if tab.get('title', '') in hidden_titles:
                continue

            folder = portal.get(tab_id, None)
            if folder is None:
                continue

            if folder.portal_type not in ['Folder', 'DigiBib']:
                continue

            tab['children'] = []

            for el in folder.contentValues():
                if not IFolder.providedBy(el):
                    continue

                if getattr(el, 'exclude_from_nav', False):
                    continue

                try:
                    tab['children'].append(el)
                except:
                    pass

        return tabs
