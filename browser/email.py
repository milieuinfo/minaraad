from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class EmailOutView(BrowserView):
    
    def __init__(self, *args, **kwargs):
        BrowserView.__init__(self, *args, **kwargs)
        
    def __call__(self):
        return self.index(template_id='email_out')
    
    def defaultTo(self):
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        
        return getattr(member, 'email', '')
