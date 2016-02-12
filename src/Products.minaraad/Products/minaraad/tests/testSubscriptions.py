from zope.component import getMultiAdapter
from zope.publisher.browser import setDefaultSkin
from zope.publisher.browser import TestRequest

from Products.minaraad.subscriptions import SubscriptionManager
from Products.minaraad.tests.MainTestCase import MainTestCase


class testSubscriptions(MainTestCase):
    """ Test cases for the generic Subscriptions of the product
    """

    def afterSetUp(self):
        membership = self.portal.portal_membership
        membership.addMember('member', 'secret', ['Member'], [])

    def test_subscriptionManager(self):
        self.login('member')

        sm = SubscriptionManager(self.portal)

        for subscription in sm.subscriptions:
            self.failIf(subscription.email)

        sm.subscribe('Advisory', email=True)

        for subscription in sm.subscriptions:
            if subscription.id == 'Advisory':
                self.failUnless(subscription.email)
            else:
                self.failIf(subscription.email)

        for subscription in sm.subscriptions:
            if subscription.id == 'Advisory':
                self.failUnless(subscription.email)
            else:
                self.failIf(subscription.email)

        self.logout()

    def test_browserSaveSubscriptions(self):
        self.login('member')

        sm = SubscriptionManager(self.portal)

        request = TestRequest()
        setDefaultSkin(request)
        view = getMultiAdapter((self.portal, request),
                               name='subscriptions_config.html')

        for x in view.subscriptions():
            self.failIf(x['subscribed_email'])

        # string values here mean nothing, the parameter just needs to
        # be in the request.
        request = TestRequest(form={'email_Advisory': 'yes',
                                    'email_Study': 'yes'})
        view = getMultiAdapter((self.portal, request),
                               name='subscriptions_config.html')
        view._saveSubscriptions()

        for x in sm.subscriptions:
            if x.id in ('Advisory', 'Study'):
                self.failUnless(x.email)
            else:
                self.failIf(x.email)

        self.logout()

    def test_browserSubscriptions(self):
        self.login('member')

        request = TestRequest()
        setDefaultSkin(request)
        view = getMultiAdapter((self.portal, request),
                               name='subscriptions_config.html')

        sm = SubscriptionManager(self.portal)
        subscriptions = view.subscriptions()

        self.failUnless(len(sm.subscriptions) == len(subscriptions))

        subDict = {}
        for x in subscriptions:
            subDict[x['id']] = x

        for x in sm.subscriptions:
            self.failUnless(x.id in subDict)

        self.logout()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testSubscriptions))
    return suite
