from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.minaraad.themes import ThemeManager
from Products.minaraad.subscriptions import SubscriptionManager, \
                                            Subscription
from StringIO import StringIO
#from Products.minaraad.browser.subscribers import ExportSubscribersView


class AbstractView(BrowserView):
    def __init__(self, context, request):
        self.request = request
        self._context = [context]
        self._buildReferral()

    def _getContext(self):
        return self._context[0]
    context = property(_getContext)

    def _buildReferral(self):
        self.referring_url = (self.request.get('referring_url', None) or
                              self.request.get('HTTP_REFERER', None) or
                              self.context.absolute_url())
        pos = self.referring_url.find('?')
        if pos > -1:
            self.referring_url = self.referring_url[:pos]
        
class MinaraadConfigletView(AbstractView):
    
    def __init__(self, context, request):
        AbstractView.__init__(self, context, request)
        self.themeManager = ThemeManager(context)
    
    def __call__(self):
        request = self.request
        response = request.response

        if request.get('form.button.Add', None):
            self._addTheme()
            return response.redirect(self.referring_url+
                                     '?portal_status_message=Theme+added')
        elif request.get('form.button.Save', None):
            self._saveThemes()
            return response.redirect(self.referring_url+
                                     '?portal_status_message=Themes+saved')
        elif request.get('form.button.Delete', None):
            self._deleteThemes()
            return response.redirect(self.referring_url+
                                     '?portal_status_message=Themes+deleted')
        
        return self.index()
    
    def themes(self):
        items = self.themeManager.themes
        isEditing = self.request.get('form.button.Edit', None) is not None
        return [{'id': id, 'Title': title} for id,title in items
                if (not isEditing) or self.request.get('theme_%i'%id, None)]
                
    def showEditableFields(self):
        return self.request.get('form.button.Edit', None) is not None

    def _addTheme(self):
        themeName = self.request.get('theme_name', None)
        self.themeManager.addTheme(themeName)
        

    def _saveThemes(self):
        editedThemes = []
        for id, title in self.themeManager.themes:
            title = self.request.get('theme_%i' % id, title)
            editedThemes.append((id, title))
            
        self.themeManager.themes = editedThemes
        
    def _deleteThemes(self):
        editedThemes = []
        for id, title in self.themeManager.themes:
            if not self.request.get('theme_%i' % id, None):
                editedThemes.append((id, title))
            
        self.themeManager.themes = editedThemes


class SubscriptionsConfigletView(AbstractView):
    
    def __init__(self, context, request):
        AbstractView.__init__(self, context, request)
        self.subscriptionManager = SubscriptionManager(self.context)
        self.themeManager = ThemeManager(self.context)

    def __call__(self):
        request = self.request
        response = request.response

        if request.get('form.button.Save', None):
            self._saveSubscriptions()
            return response.redirect(self.referring_url+
                                     '?portal_status_message=Subscriptions+saved')
        
        return self.index()

    def _getThemeTitle(self, id):
        # get rid of 'theme_' prefix
        id = id[6:]
        
        return self.themeManager.getThemeTitle(id)
    
    def subscriptions(self):
        
        sm = self.subscriptionManager
        items = sm.subscriptions
        subscriptions = []
        for item in items:
            sub = {'id': item.id,
                   'subscribed_email': item.email,
                   'subscribed_post': item.post}
            subscriptions.append(sub)
            
            title = self._getThemeTitle(item.id)
            if title:
                sub['level'] = 1
                sub['category'] = 'Hearing'
                sub['can_post'] = False
                sub['can_email'] = True
            else:
                sub['level'] = 0
                sub['category'] = ''
                sub['can_post'] = sm.canSubscribePost(item.id)
                sub['can_email'] = sm.canSubscribeEmail(item.id)

            sub['Title'] = title or item.id
        
        return subscriptions
    
    def _saveSubscriptions(self):

        subscriptions = self.subscriptionManager.subscriptions
        for sub in subscriptions:
            sub.post = not not self.request.get('post_'+sub.id, False)
            sub.email = not not self.request.get('email_'+sub.id, False)

        self.subscriptionManager.subscriptions = subscriptions

class SubscribersConfigletView(AbstractView):

    def __init__(self, context, request):
        AbstractView.__init__(self, context, request)
        tool = getToolByName(self.context, 'portal_url')
        portal = tool.getPortalObject()
        self.subscriptionManager = SubscriptionManager(portal)
        self._subManager = self.subscriptionManager
        self.themeManager = ThemeManager(portal)

    def __call__(self):
        request = self.request
        subject = request.get('sub', None)
        if request.get('form.button.ExportEmail', None) is not None:
            return self.buildSubscriberCSV('email', subject)
        elif request.get('form.button.ExportPost', None) is not None:
            return self.buildSubscriberCSV('post', subject)
        else:
            return self.index(template_id='subscribers_config.html')

    def _getThemeTitle(self, id):
        id = id[6:]
        
        return self.themeManager.getThemeTitle(id)
    
    #Get subscriptions
    def subscriptions(self):
        sm = self.subscriptionManager
        items = sm.subscriptions
        subscriptions = []
        for item in items:
            sub = {'id': item.id,
                   'subscribed_email': item.email,
                   'subscribed_post': item.post}
            subscriptions.append(sub)
            
            title = self._getThemeTitle(item.id)
            if title:
                sub['level'] = 1
                sub['category'] = 'Hearing'
                sub['can_post'] = False
                sub['can_email'] = True
            else:
                sub['level'] = 0
                sub['category'] = ''
                sub['can_post'] = sm.canSubscribePost(item.id)
                sub['can_email'] = sm.canSubscribeEmail(item.id)

            sub['Title'] = title or item.id
        
        return subscriptions

    #get Members of the subscriptions
    def getMembersOfSubscriptions(self, id):
        sm = self.subscriptionManager
        subscribers = sm.emailSubscribers(id)
        for subscriber in sm.postSubscribers(id):
            if subscriber not in subscribers:
                subscribers.append(subscriber)
        return subscribers

    def getSubscriptionType(self, memberid, subscriptionid):
        sm = self.subscriptionManager
        returnString = ''
        if memberid in sm.emailSubscribers(subscriptionid):
            returnString += 'email'
        if memberid in sm.postSubscribers(subscriptionid):
            if returnString != '':
                returnString += ', post'
            else:
                returnString += 'post'
        return returnString

    def buildSubscriberCSV(self, type_, subject):
        subscriberId = subject
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
