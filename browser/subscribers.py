from StringIO import StringIO
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.minaraad.subscriptions import SubscriptionManager

class ExportSubscribersView(BrowserView):
    
    def __init__(self, *args, **kwargs):
        BrowserView.__init__(self, *args, **kwargs)
        
        tool = getToolByName(self.context, 'portal_url')
        portal = tool.getPortalObject()
        self._subManager = SubscriptionManager(portal)
    
    def __call__(self):
        
        request = self.request
        if request.get('form.button.ExportEmail', None) is not None:
            return self.buildSubscriberCSV('email')
        elif request.get('form.button.ExportPost', None) is not None:
            return self.buildSubscriberCSV('post')

        return self.index(template_id='export_subscribers')

    def buildSubscriberCSV(self, type_):
        obj = self.context.aq_explicit
        subscriberId = obj.__class__.__name__
        ploneUtils = getToolByName(self.context, 'plone_utils')
        safeSubscriberId = ploneUtils.normalizeString(subscriberId).lower()
        
        portalProperties = getToolByName(self.context, 
                                         'portal_properties')
        siteProperties = portalProperties.site_properties
        charset = siteProperties.getProperty('default_charset')
        
        out = StringIO()
        
        fields = (('gender', 'Gender'), 
                  ('firstname', 'First Name'),
                  ('fullname', 'Last Name'),
                  ('company', 'Company'),
                  ('street', 'Street'),
                  ('housenumber', 'House Number'),
                  ('bus', 'Bus'),
                  ('zipcode', 'Zip Code'),
                  ('city', 'City'),
                  ('country', 'Country'),
                  ('other_country', 'Other country'))
        
        for pos, field in enumerate(fields):
            id, title = field
            
            out.write(u'"%s"' % title)
            if pos < len(fields)-1:
                out.write(u',')
            
        out.write(u'\n')
        
        if type_ == 'post':
            subscribers = self._subManager.postSubscribers(subscriberId)
        elif type_ == 'email':
            subscribers = self._subManager.emailSubscribers(subscriberId)
        else:
            raise ValueError("The 'type' argument must be either " \
                             "'post' or 'email'")
        
        for subscriber in subscribers:
            for pos, field in enumerate(fields):
                id, title = field
                
                value = unicode(subscriber.getProperty(id, ''), charset)
                value = value.replace(u'"', u'""')
                out.write(u'"%s"' % value)
        
                if pos < len(fields)-1:
                    out.write(u',')

            out.write(u'\n')
            
        response = self.request.response
        response['Content-Type'] = \
            'application/vnd.ms-excel; charset=%s' % charset
        response['Content-Disposition'] = \
            'attachment; filename=%s-subscribers.csv' % safeSubscriberId

        return out.getvalue().encode(charset)
