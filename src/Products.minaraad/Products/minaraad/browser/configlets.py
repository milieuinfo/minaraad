from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.minaraad.browser.utils import buildCSV
from Products.minaraad.subscriptions import SUBSCRIPTIONS_EMAIL
from Products.minaraad.subscriptions import SubscriptionManager
from Products.minaraad.themes import ThemeManager
from Products.statusmessages.interfaces import IStatusMessage
import logging

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
            message = u"Thema toegevoegd"
            IStatusMessage(request).addStatusMessage(message, type="info")
            return response.redirect(self.referring_url)
        elif request.get('form.button.Save', None):
            self._saveThemes()
            message = u"Thema opgeslagen"
            IStatusMessage(request).addStatusMessage(message, type="info")
            return response.redirect(self.referring_url)
        elif request.get('form.button.Delete', None):
            self._deleteThemes()
            message = u"Thema verwijderd"
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


class SubscriptionsConfigletView(AbstractView):
    """Configlet for an end user to manage his own subscriptions.
    """

    def __init__(self, context, request):
        AbstractView.__init__(self, context, request)
        self.subscriptionManager = SubscriptionManager(context)
        self.themeManager = ThemeManager(context)

    def __call__(self):
        request = self.request
        response = request.response

        if request.get('form.button.Save', None):
            self._saveSubscriptions()
            message = u"Abonnementen zijn bewaard"
            IStatusMessage(request).addStatusMessage(message, type="info")
            return response.redirect(self.referring_url)

        return self.index()

    def _getThemeTitle(self, id):
        return self.themeManager.getThemeTitle(id)

    def themes(self, memberid=None):
        sm = self.subscriptionManager
        if memberid is not None:
            subscribed_themes = sm.getThemesForMemberId(memberid)
        else:
            subscribed_themes = sm.themes

        themes = []
        for id, title in self.themeManager.themes:
            subscribed = str(id) in subscribed_themes
            theme = dict(id=id,
                         title=title,
                         subscribed=subscribed)
            themes.append(theme)
            long_description = LONGDESC.get(id)
            if long_description:
                theme['long'] = long_description
        return themes

    def subscriptions(self, memberid=None):
        sm = self.subscriptionManager
        if memberid is not None:
            items = sm.getSubscriptionsForMemberId(memberid)
        else:
            items = sm.subscriptions

        subscriptions = []
        for item in items:
            sub = dict(
                id=item.id,
                subscribed_email=item.email,
                can_email=sm.canSubscribeEmail(item.id),
                Title=item.id,
            )
            subscriptions.append(sub)
        return subscriptions

    def _saveSubscriptions(self):
        subscriptions = self.subscriptionManager.subscriptions
        for sub in subscriptions:
            sub.email = not not self.request.get('email_' + sub.id, False)

        self.subscriptionManager.subscriptions = subscriptions
        self.subscriptionManager.themes = self.request.form.get('themes', [])


class SubscribersConfigletView(AbstractView):
    """Configlet for a manager that shows lots of Excel export buttons.
    """

    def __init__(self, context, request):
        AbstractView.__init__(self, context, request)
        tool = getToolByName(context, 'portal_url')
        portal = tool.getPortalObject()
        self.sm = SubscriptionManager(portal)
        self.tm = ThemeManager(portal)

    def __call__(self):
        form = self.request.form

        themes = form.get('themes', [])
        for key in form.keys():
            if key == 'export_all_members':
                return self.buildMembersCSV()
            if key.startswith('export_email_'):
                contenttype = key.replace('export_email_', '')
                return self.buildSubscriberCSV(contenttype, themes)
        return self.index(template_id='subscribers_config.html')

    def themes(self):
        for id, title in self.tm.themes:
            yield dict(id=id, title=title)

    def subscriptions(self):
        allNames = SUBSCRIPTIONS_EMAIL

        for name in allNames:
            sub = dict(
                id=name,
                can_email=(name in SUBSCRIPTIONS_EMAIL),
            )
            yield sub

    def buildSubscriberCSV(self, contenttype, themes):
        context = aq_inner(self.context)
        ploneUtils = getToolByName(context, 'plone_utils')
        safe_contenttype = ploneUtils.normalizeString(contenttype).lower()

        subscribers = []
        query = self.sm.emailSubscribers

        for subscriber in query(contenttype, themes=themes):
            if subscriber not in subscribers:
                subscribers.append(subscriber)

        logger.info("Exporting cvs for %s subscribers for %s (themes=%r)",
                    len(subscribers), contenttype, themes)

        return buildCSV(context,
                        subscribers,
                        filename='%s-subscribers.csv' % safe_contenttype)

    def buildMembersCSV(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        subscribers = mtool.listMembers()
        logger.info("Exporting cvs for all %s members.", len(subscribers))
        return buildCSV(context, subscribers, filename='all-members.csv')
