import logging

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from Products.minaraad.subscriptions import SubscriptionManager
from Products.minaraad.browser.utils import buildCSV
from Products.minaraad.subscriptions import THEME_FILTERED
from Products.minaraad.subscriptions import SUBSCRIPTIONS_EMAIL

logger = logging.getLogger('exportsubscribers')


class ExportSubscribersView(BrowserView):

    def __init__(self, *args, **kwargs):
        BrowserView.__init__(self, *args, **kwargs)
        tool = getToolByName(self.context, 'portal_url')
        portal = tool.getPortalObject()
        self.sm = SubscriptionManager(portal)
        obj = self.context.aq_explicit
        self.contenttype = obj.__class__.__name__

    def __call__(self):
        """Return template with form or return csv."""
        request = self.request
        if request.get('form.button.ExportEmail', None) is not None:
            return self.buildSubscriberCSV()

        return self.index(template_id='export_subscribers')

    def show_theme_warning(self):
        """A theme field was added to two contenttypes, warn if it is None."""
        if self.contenttype in ['Study', 'Advisory']:
            if self.context.getTheme() is None:
                return True
        # In all other cases, no warning is needed.
        return False

    def can_email(self):
        return self.contenttype in SUBSCRIPTIONS_EMAIL

    def buildSubscriberCSV(self):
        ploneUtils = getToolByName(self.context, 'plone_utils')
        safeSubscriberId = ploneUtils.normalizeString(self.contenttype).lower()

        themes = None
        if self.contenttype in THEME_FILTERED:
            themes = self.context.get_all_themes()

        subscribers = self.sm.emailSubscribers(self.contenttype,
                                               themes=themes)

        logger.info("Exporting cvs for %s subscribers for %s (themes=%r)",
                    len(subscribers), self.contenttype, themes)
        return buildCSV(self.context,
                        subscribers,
                        filename='%s-subscribers.csv' % safeSubscriberId)
