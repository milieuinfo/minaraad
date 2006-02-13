from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class MinaraadConfigletView(BrowserView):
    def themes(self):
        propsTool = getToolByName(self.context, 'portal_properties')
        sheet = propsTool.minaraad_properties

        themes = []
        for x in sheet.getProperty('themes'):
            pos = x.find('/')
            d = {'id': x[:pos], 'Title': x[pos+1:]}
            themes.append(d)
            
        return themes
