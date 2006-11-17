'''/
'''

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class GlobalView(BrowserView):
    """Helpers used from the global templates
    """

    def isHomePage(self):
        'XXX'
        context = self.context
        portalroot = getToolByName(context, 'portal_url').getPortalObject()
        if context == portalroot:
            return True
        defaultpage = portalroot.restrictedTraverse(portalroot.getDefaultPage())
        return context == defaultpage
