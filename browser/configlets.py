from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class MinaraadConfigletView(BrowserView):
    
    def __call__(self):
        self._buildReferral()

        request = self.request
        response = request.response

        themeName = request.get('theme_name', None)
        if themeName:
            self.addTheme(themeName)
            return response.redirect(self.referring_url+
                                     '?portal_status_message=Theme+added')
        elif request.get('form.button.Save', None):
            self.saveThemes()
            return response.redirect(self.referring_url+
                                     '?portal_status_message=Themes+saved')
        elif request.get('form.button.Delete', None):
            self.deleteThemes()
            return response.redirect(self.referring_url+
                                     '?portal_status_message=Themes+deleted')
        
        
        return self.index()
    
    def _buildReferral(self):
        self.referring_url = (self.request.get('referring_url', None) or
                              self.request.get('HTTP_REFERER', None) or
                              self.context.absolute_url())
        pos = self.referring_url.find('?')
        if pos > -1:
            self.referring_url = self.referring_url[:pos]
        
    def themes(self):
        propsTool = getToolByName(self.context, 'portal_properties')
        sheet = propsTool.minaraad_properties

        themes = []
        isEditing = self.request.get('form.button.Edit', None) is not None
        for x in sheet.getProperty('themes'):
            pos = x.find('/')
            id = x[:pos]
            if (not isEditing) or self.request.get('theme_'+id, None):
                d = {'id': id, 'Title': x[pos+1:]}
                themes.append(d)
            
        return themes

    def nextThemeId(self):
        themes = self.themes()
        ids = [int(x['id']) for x in themes]
        return max(ids) + 1

    def addTheme(self, theme):
        propsTool = getToolByName(self.context, 'portal_properties')
        sheet = propsTool.minaraad_properties
        
        newId = self.nextThemeId()
        newLine = "%i/%s" % (newId, theme)
        newThemes = sheet.getProperty('themes') + (newLine,)
        sheet.manage_changeProperties({'themes': newThemes})
        
    def saveThemes(self):
        propsTool = getToolByName(self.context, 'portal_properties')
        sheet = propsTool.minaraad_properties

        editedThemes = []
        for x in sheet.getProperty('themes'):
            pos = x.find('/')
            id = x[:pos]
            value = x[pos+1:]

            value = self.request.get('theme_'+id, value)
            editedThemes.append('%s/%s' % (id, value))
            
        sheet.manage_changeProperties({'themes': editedThemes})
        
    def deleteThemes(self):
        propsTool = getToolByName(self.context, 'portal_properties')
        sheet = propsTool.minaraad_properties

        editedThemes = []
        for x in sheet.getProperty('themes'):
            pos = x.find('/')
            id = x[:pos]
            value = x[pos+1:]

            if not self.request.get('theme_'+id, None):
                editedThemes.append('%s/%s' % (id, value))
            
        sheet.manage_changeProperties({'themes': editedThemes})
        
    def showEditableFields(self):
        return self.request.get('form.button.Edit', None) is not None

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

