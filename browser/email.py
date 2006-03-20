from configlets import AbstractView
from Products.CMFCore.utils import getToolByName

class EmailOutView(AbstractView):
    
    def __call__(self):
        request = self.request
        response = request.response
        
        if request.get('send', None) is not None:
            additionalMembers = [mem for mem in
                                 self.request.get('to', '').split(',')
                                 if mem]
            testing = bool(int(self.request.get('send_as_test', "0")))
            text = self.request.get('additional', None)
            
            self.context.email(text=text, 
                               testing=testing, 
                               additionalMembers=additionalMembers)
            
            return response.redirect(self.referring_url+
                                     '?portal_status_message=E-mail+Sent')
        
        return self.index(template_id='email_out')
    
    def defaultTo(self):
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return str(member)

    def canSend(self):
        return self.context.getEmailSent() is None
    
    def sentDate(self):
        localize = self.context.toLocalizedTime
        return localize(time=self.context.getEmailSent(), long_format=True)
