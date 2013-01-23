from plone.portlets.interfaces import IPortletDataProvider
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base

from Products.minaraad import MinaraadMessageFactory as _

class ILinkedInPortlet(IPortletDataProvider):
    """ A portlet displaying the linkedIn link.
    """


class Assignment(base.Assignment):
    implements(ILinkedInPortlet)

    @property
    def title(self):
        return _(u"LinkedIn")


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('portlet_linkedin.pt')


class AddForm(base.NullAddForm):
    form_fields = form.Fields(ILinkedInPortlet)
    label = _(u"Add linkedin Portlet")
    description = _(u"This portlet shows the linkedIn link")

    def create(self):
        return Assignment()
