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
        for x in sheet.getProperty('themes'):
            pos = x.find('/')
            d = {'id': x[:pos], 'Title': x[pos+1:]}
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
        
    