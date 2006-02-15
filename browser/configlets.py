from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.minaraad import themes

class MinaraadConfigletView(BrowserView):
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.themeManager = themes.ThemeManager(context)
    
    def __call__(self):
        self._buildReferral()
        
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
        themes = self.themeManager.themes
        isEditing = self.request.get('form.button.Edit', None) is not None
        return [{'id': id, 'Title': title} for id,title in themes 
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

    def _buildReferral(self):
        self.referring_url = (self.request.get('referring_url', None) or
                              self.request.get('HTTP_REFERER', None) or
                              self.context.absolute_url())
        pos = self.referring_url.find('?')
        if pos > -1:
            self.referring_url = self.referring_url[:pos]
        

SUBSCRIPTIONS_EMAIL = ('Advisory', 'Study', 'Hearing', 'Newsletter', 
                       'Pressrelease', 'AnnualReport')
SUBSCRIPTIONS_POST = ('Advisory', 'Study', 'AnnualReport')

class SubscriptionsConfigletView(BrowserView):
    
    def __init__(self, context, request):
        self.request = request
        self._context = [context]

    def _getContext(self):
        return self._context[0]
    context = property(_getContext)

    def themes(self):
        themeManager = themes.ThemeManager(context)
        themes = themeManager.themes
        return [{'id': id, 'Title': title} for id,title in themes]

    def getSubscriptions(self):
        tool = getToolByName(self.context, 'portal_membership')
        member = tool.getAuthenticatedMember()
        
        prop = member.getProperty('subscriptions', [])

        subscriptions = [{'id': x, 'Title': x, 'subscribed': x in prop} 
                         for x in SUBSCRIPTIONS_EMAIL]
        
        return subscriptions
    
    def getSubscriptionsPost(self):
        tool = getToolByName(self.context, 'portal_membership')
        member = tool.getAuthenticatedMember()
        
        prop = member.getProperty('subscriptions_post', [])

        subscriptions_post = [{'id': x, 'Title': x, 'subscribed': x in prop} 
                         for x in SUBSCRIPTIONS_POST]
        
        return subscriptions_post
    
    def setSubscriptions(self, subscriptions):
        tool = getToolByName(self.context, 'portal_membership')
        member = tool.getAuthenticatedMember()

        member.manage_changeProperties({'subscriptions': subscriptions})
        member.manage_changeProperties({'subscriptions_post': subscriptions_post})

