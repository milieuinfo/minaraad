from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import login as p_login
from zope.interface import implements


class ILoginPortlet(p_login.ILoginPortlet):
    pass


class Assignment(p_login.Assignment):
    implements(ILoginPortlet)


class Renderer(p_login.Renderer):
    _template = ViewPageTemplateFile('portlet_login.pt')


class AddForm(p_login.AddForm):
    def create(self):
        return Assignment()
