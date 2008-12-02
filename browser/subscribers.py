from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.minaraad.subscriptions import SubscriptionManager
from Products.minaraad.browser.utils import buildCSV


class ExportSubscribersView(BrowserView):

    def __init__(self, *args, **kwargs):
        BrowserView.__init__(self, *args, **kwargs)

        tool = getToolByName(self.context, 'portal_url')
        portal = tool.getPortalObject()
        self._subManager = SubscriptionManager(portal)

    def __call__(self):

        request = self.request
        if request.get('form.button.ExportEmail', None) is not None:
            return self.buildSubscriberCSV('email')
        elif request.get('form.button.ExportPost', None) is not None:
            return self.buildSubscriberCSV('post')

        return self.index(template_id='export_subscribers')

    def buildSubscriberCSV(self, type_):
        obj = self.context.aq_explicit
        subscriberId = obj.__class__.__name__
        ploneUtils = getToolByName(self.context, 'plone_utils')
        safeSubscriberId = ploneUtils.normalizeString(subscriberId).lower()

        if type_ == 'post':
            subscribers = self._subManager.postSubscribers(subscriberId)
        elif type_ == 'email':
            subscribers = self._subManager.emailSubscribers(subscriberId)
        else:
            raise ValueError("The 'type' argument must be either " \
                             "'post' or 'email'")
        return buildCSV(self.context,
                        subscribers,
                        filename='%s-subscribers.csv' % safeSubscriberId)
