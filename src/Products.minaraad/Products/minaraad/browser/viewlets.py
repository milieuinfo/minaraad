from zope.component.hooks import getSite
from plone.app.layout.viewlets.common import GlobalSectionsViewlet

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class MinaGlobalSectionsViewlet(GlobalSectionsViewlet):
    index = ViewPageTemplateFile('sections.pt')

    def get_portal_tabs(self):
        portal = getSite()
        tabs = self.portal_tabs

        for tab in tabs:
            tab_id = tab.get('id', None)
            folder = portal.get(tab_id, None)

            if folder is None:
                continue

            tab['children'] = []

            for el in folder.contentValues():
                try:
                    tab['children'].append(el)
                except:
                    pass

        print tabs
        return tabs
