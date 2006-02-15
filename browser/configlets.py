from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.minaraad.themes import ThemeManager

class AbstractConfigletView(BrowserView):
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self._buildReferral()

    def _buildReferral(self):
        self.referring_url = (self.request.get('referring_url', None) or
                              self.request.get('HTTP_REFERER', None) or
                              self.context.absolute_url())
        pos = self.referring_url.find('?')
        if pos > -1:
            self.referring_url = self.referring_url[:pos]
        
class MinaraadConfigletView(AbstractConfigletView):
    
    def __init__(self, context, request):
        AbstractConfigletView.__init__(self, context, request)
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


SUBSCRIPTIONS_ALL = ('Advisory', 'Study', 'Newsletter', 
                     'Pressrelease', 'AnnualReport')
SUBSCRIPTIONS_POST = ('Advisory', 'Study', 'AnnualReport')

class SubscriptionsConfigletView(AbstractConfigletView):
    
    def __init__(self, context, request):
        self.request = request
        self._context = [context]
        self._buildReferral()

    def _getContext(self):
        return self._context[0]
    context = property(_getContext)

    def __call__(self):
        request = self.request
        response = request.response

        if request.get('form.button.Save', None):
            self._saveSubscriptions()
            return response.redirect(self.referring_url+
                                     '?portal_status_message=Subscriptions+saved')
        
        return self.index()

    def subscriptions(self):
        tool = getToolByName(self.context, 'portal_membership')
        member = tool.getAuthenticatedMember()
        
        prop = member.getProperty('subscriptions', [])

        themeManager = ThemeManager(self.context)
        themeItems = [{'id': 'theme_'+str(id), 
                       'Title': title,
                       'level': 1,
                       'category': 'Hearing',
                       'can_post': False, 
                       'can_email': True,
                       'subscribed_email': False,
                       'subscribed_post': False}
                      for id,title in themeManager.themes]

        subscriptions = [{'id': x, 
                          'Title': x, 
                          'level': 0,
                          'subscribed_post': False,
                          'subscribed_email': False,
                          'can_post': x in SUBSCRIPTIONS_POST,
                          'can_email': True} 
                         for x in SUBSCRIPTIONS_ALL] + themeItems

        subDict = {}
        
        for x in prop:
            id, email, post = x.split('/')
            subDict[id] = {'subscribed_email': bool(int(email)),
                           'subscribed_post': bool(int(post))}

        for x in subscriptions:
            d = subDict.get(x['id'], None)
            if d:
                x['subscribed_email'] = d['subscribed_email']
                x['subscribed_post'] = d['subscribed_post']
        
        return subscriptions
    
    def _saveSubscriptions(self):
        subs = {}
        for x in self.request.form.keys():
            if x.startswith('post_'):
                id = x[5:]
                d = subs.get(id, {})
                subs[id] = d
                d['id'] = id
                d['subscribed_post'] = True
                d['subscribed_email'] = d.get('subscribed_email', False)
            elif x.startswith('email_'):
                id = x[6:]
                d = subs.get(id, {})
                subs[id] = d
                d['id'] = id
                d['subscribed_email'] = True
                d['subscribed_post'] = d.get('subscribed_post', False)

        self.setSubscriptions(subs.values())
    
    def setSubscriptions(self, subscriptions):
        tool = getToolByName(self.context, 'portal_membership')
        member = tool.getAuthenticatedMember()

        subscriptions = ['%s/%i/%i' % (x['id'], 
                                       x['subscribed_email'], 
                                       x['subscribed_post']) 
                         for x in subscriptions]

        member.setProperties(subscriptions=subscriptions)

