import logging

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from Products.minaraad.themes import ThemeManager

logger = logging.getLogger('configlets')


LONGDESC = {
    21: ('Europese, Belgische, Vlaamse regelgeving &amp; planning, '
         'duurzame ontwikkeling, begroting'),
    22: 'Heffingen, steun, handhaving, vergunningen, m.e.r.',
    23: 'Lucht, bodem, afval, energie',
    # Nothing for 24
    25: 'Landbouw, natuur, bos, jacht, erkenningen',
    # Nothing for 26
    27: 'NME, samenwerkingsovereenkomst',
}


class AbstractView(BrowserView):

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self._buildReferral()

    def _buildReferral(self):
        context = aq_inner(self.context)
        self.referring_url = (self.request.get('referring_url', None) or
                              self.request.get('HTTP_REFERER', None) or
                              context.absolute_url())
        pos = self.referring_url.find('?')
        if pos > -1:
            self.referring_url = self.referring_url[:pos]


class MinaraadConfigletView(AbstractView):
    """Configlet for a manager to manage themes.
    """

    def __init__(self, context, request):
        AbstractView.__init__(self, context, request)
        self.themeManager = ThemeManager(context)

    def __call__(self):
        request = self.request
        response = request.response

        if request.get('form.button.Add', None):
            self._addTheme()
            message = u"Werkveld toegevoegd"
            IStatusMessage(request).addStatusMessage(message, type="info")
            return response.redirect(self.referring_url)
        elif request.get('form.button.Save', None):
            self._saveThemes()
            message = u"Werkvelden opgeslagen"
            IStatusMessage(request).addStatusMessage(message, type="info")
            return response.redirect(self.referring_url)
        elif request.get('form.button.Delete', None):
            self._deleteThemes()
            message = u"Werkveld verwijderd"
            IStatusMessage(request).addStatusMessage(message, type="info")
            return response.redirect(self.referring_url)

        return self.index()

    def themes(self):
        items = self.themeManager.themes
        isEditing = self.request.get('form.button.Edit', None) is not None
        return [{'id': id, 'Title': title} for id, title in items
                if (not isEditing) or self.request.get('theme_%i' % id, None)]

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
