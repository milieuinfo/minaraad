from zope.app import zapi
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
        view = zapi.getMultiAdapter((self.portal, request),
                                    name='subscriptions_config.html')

        for x in view.subscriptions():
            self.failIf(x['subscribed_email'])

        # string values here mean nothing, the parameter just needs to
        # be in the request.
        request = TestRequest(form={'email_Advisory': 'yes',
                                    'email_Study': 'yes'})
        view = zapi.getMultiAdapter((self.portal, request),
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
        view = zapi.getMultiAdapter((self.portal, request),
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

    def test_exportSubscribers(self):
        self.loginAsPortalOwner()
        self.portal.adviezen.adv_2006.invokeFactory('Advisory', 'myadvisory')
        advisory = self.portal.adviezen.adv_2006.myadvisory
        advisory.setTheme(1)
        advisory.reindexObject()

        self.login('member')
        member = self.portal.portal_membership.getAuthenticatedMember()
        props = dict(
            gender="Yes",
            firstname="John",
            fullname="Doe",
            company="Doe Enterprises",
            street="Doe Street",
            housenumber="23",
            bus="Bus C",
            zipcode="007",
            city="Rotterdam",
            country="The Netherlands",
            )

        member.setProperties(**props)

        sm = SubscriptionManager(self.portal)
        request = self.portal.REQUEST

        request['form.button.ExportEmail'] = True

        view = zapi.getMultiAdapter((advisory, request),
                                    name='export_subscribers')

        HEADER_FIELDS = ("Aanhef", "Voornaam", "Achternaam", "Organisatie",
                         "Functie", "Straat", "Huisnummer", "Bus", "Postcode",
                         "Woonplaats", "Land", "Ander land", "Telefoonnummer",
                         "E-mail")
        headingLine = ''
        for x in HEADER_FIELDS:
            headingLine += '"%s",' % x
        headingLine = headingLine[:-1] + '\n'
        self.assertEquals(view(), headingLine)

        # let's do the actual subscription of our member
        sm.subscribe('Advisory', email=True)
        sm.themes = [1]

        lines = view().split('\n')
        self.assertEquals(lines[1], '"Yes","John","Doe","Doe Enterprises",'
                          '"","Doe Street","23","Bus C","007",'
                          '"Rotterdam","The Netherlands","","",""')

        # let's make some assertions about the response
        self.assertEquals(
            request.response['content-type'],
            'application/vnd.ms-excel; charset=iso-8859-1')

        self.assertEquals(
            request.response['content-disposition'],
            'attachment; filename=advisory-subscribers.csv')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testSubscriptions))
    return suite
