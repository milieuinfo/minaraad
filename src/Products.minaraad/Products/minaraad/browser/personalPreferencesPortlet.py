from plone.portlets.interfaces import IPortletDataProvider
from zope.formlib import form
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base

from Products.minaraad import MinaraadMessageFactory as _


class IPersonalPreferencesPortlet(IPortletDataProvider):
    """A portlet displaying the personal preferences.
    """


class Assignment(base.Assignment):
    implements(IPersonalPreferencesPortlet)

    @property
    def title(self):
        return _(u"Personal Preferences")


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('portlet_personalprefs.pt')


class AddForm(base.NullAddForm):
    form_fields = form.Fields(IPersonalPreferencesPortlet)
    label = _(u"Add Personal Preferences Portlet")
    description = _(u"This portlet shows links for editing your preferences")

    def create(self):
        return Assignment()
