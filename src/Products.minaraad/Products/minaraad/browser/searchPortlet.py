from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import search as p_search
from zope.interface import implements


class ISearchPortlet(p_search.ISearchPortlet):
    pass


class Assignment(p_search.Assignment):
    implements(ISearchPortlet)


class Renderer(p_search.Renderer):
    _template = ViewPageTemplateFile('portlet_search.pt')


class AddForm(p_search.AddForm):
    def create(self, data):
        return Assignment()


class EditForm(p_search.EditForm):
    pass
