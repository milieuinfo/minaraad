from configlets import AbstractView
from Products.CMFCore.utils import getToolByName
import urllib

class EmailOutView(AbstractView):
    
    def __call__(self):
        request = self.request
        response = request.response
        
        if request.get('send', None) is not None:
            additionalMembers = [mem.strip() for mem in
                                 self.request.get('to', '').split(',')
                                 if mem]
            testing = bool(int(self.request.get('send_as_test', "0")))
            text = self.request.get('additional', None)
            
            failed_postings = self.context.email(text=text, 
                               testing=testing, 
                               additionalMembers=additionalMembers)
            
            if failed_postings:
                message = "E-Mail failed to following addresses: %s" % (
                    ', '.join([send_info.toAddress for send_info in failed_postings]),
                    )
            else:
                message = 'E-mail Sent'
                    
            return response.redirect('%s?portal_status_message=%s' % (self.referring_url, urllib.quote_plus(message)))
        
        return self.index(template_id='email_out')
    
    def defaultTo(self):
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return str(member)

    def canSend(self):
       # return self.context.getEmailSent() is None
       return True
    
    def sentDate(self):
        localize = self.context.toLocalizedTime
        return localize(time=self.context.getEmailSent(), long_format=True)
