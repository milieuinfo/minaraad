from Products.CMFCore.utils import getToolByName

class ThemeManager(object):

    def __init__(self, portal):
        self.portal = portal

    def nextThemeId(self):
        if not self.themes:
            # No items yet
            return 1
        highest_id = max([id for id, title in self.themes])
        return highest_id + 1

    def addTheme(self, theme, newId = None):
        propsTool = getToolByName(self.portal, 'portal_properties')
        sheet = propsTool.minaraad_properties

        if newId is None:
            newId = self.nextThemeId()

        newLine = "%i/%s" % (newId, theme)
        newThemes = sheet.getProperty('themes') + (newLine, )
        # First argument is the request, which is only interesting
        # when we want to be redirected, which we do not want.
        props = {'themes': newThemes}
        sheet.manage_changeProperties(None, **props)

    def deleteThemes(self, theme_ids):
        self._setThemes(
            [(t_id, title) for t_id, title in self._getThemes()
             if t_id not in theme_ids])

    def _setThemes(self, themes):
        lines = []
        for id, title in themes:
            lines.append('%s/%s' % (str(id), title))

        propsTool = getToolByName(self.portal, 'portal_properties')
        sheet = propsTool.minaraad_properties
        # First argument is the request, which is only interesting
        # when we want to be redirected, which we do not want.
        props = {'themes': lines}
        sheet.manage_changeProperties(None, **props)

    def _getThemes(self):
        propsTool = getToolByName(self.portal, 'portal_properties')
        sheet = propsTool.minaraad_properties
        themes = []
        for x in sheet.getProperty('themes'):
            id, title = x.split('/')
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
