from zope.interface import implements

from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from plone.app.portlets.portlets import recent as p_recent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class IRecentPortlet(p_recent.IRecentPortlet):
    pass


class Assignment(p_recent.Assignment):
    implements(IRecentPortlet)


class Renderer(p_recent.Renderer):
    _template = ViewPageTemplateFile('portlet_recent.pt')

    @memoize
    def _data(self):
        catalog = getToolByName(self.context,
                                'portal_catalog')

        searchable_types = ['Hearing', 'Advisory',
                            'Study', 'AnnualReport',
                            'Pressrelease', 'NewsLetter',
                            'Event', 'MREvent', 'Document']

        return catalog.searchResults(portal_type=searchable_types,
                                     sort_on='effective',
                                     sort_order='reverse')[:self.data.count]

    @property
    def available(self):
        return self.data.count > 0 and \
               len(self._data())


class AddForm(p_recent.AddForm):
    def create(self, data):
        return Assignment(count=data.get('count', 5))


class EditForm(p_recent.EditForm):
    pass

