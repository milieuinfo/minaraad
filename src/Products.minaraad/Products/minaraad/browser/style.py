from zope.interface import implements
from zope.component import getMultiAdapter
from Products.TinyMCE.browser.interfaces.style import ITinyMCEStyle
from Products.TinyMCE.browser.style import TinyMCEStyle


class MinaraadTinyMCEStyle(TinyMCEStyle):
    """TinyMCE Style including minaraad css."""
    implements(ITinyMCEStyle)

    def getStyle(self):
        """Returns a stylesheet with all content styles"""
        base = super(MinaraadTinyMCEStyle, self).getStyle()
        # Add minaraad theme style.
        pps = getMultiAdapter((self.context, self.request),
                              name='plone_portal_state')
        theme_style = "%s/++theme++minaraad/css/style.css" % pps.portal_url()
        return base + "\n<!-- @import url(%s); -->" % theme_style
