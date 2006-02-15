
from Products.CMFCore.utils import getToolByName

class ThemeManager(object):
    
    def __init__(self, portal):
        self.portal = portal
    
    def nextThemeId(self):
        return max([id for id,title in self.themes]) + 1
    
    def addTheme(self, theme):
        propsTool = getToolByName(self.portal, 'portal_properties')
        sheet = propsTool.minaraad_properties
        
        newId = self.nextThemeId()
        newLine = "%i/%s" % (newId, theme)
        newThemes = sheet.getProperty('themes') + (newLine,)
        sheet.manage_changeProperties({'themes': newThemes})
        
    def _setThemes(self, themes):
        lines = []
        for id, title in themes:
            lines.append('%s/%s' % (str(id), title))
        
        propsTool = getToolByName(self.portal, 'portal_properties')
        sheet = propsTool.minaraad_properties
        sheet.manage_changeProperties({'themes': lines})

    def _getThemes(self):
        propsTool = getToolByName(self.portal, 'portal_properties')
        sheet = propsTool.minaraad_properties
    
        themes = []
        for x in sheet.getProperty('themes'):
            pos = x.find('/')
            id = x[:pos]
            title = x[pos+1:]

            themes.append((int(id), title))
            
        return themes
    
    def getThemeTitle(self, id):
        try:
            id = int(id)
            themes = self.themes
            for curId, curTitle in themes:
                if curId == id:
                    return curTitle
        except ValueError:
            pass
        
        return None
    
    themes = property(_getThemes, _setThemes)
    