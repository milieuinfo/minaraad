# File: testSubscriptions.py
#
# Copyright (c) 2006 by Zest Software
# Generator: ArchGenXML Version 1.4.1 svn/devel
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Rocky Burt <r.burt@zestsoftware.nl>"""
__docformat__ = 'plaintext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

#
# Subscriptions tests
#

import os, sys
from Testing import ZopeTestCase
from Products.minaraad.tests.MainTestCase import MainTestCase
from zope.app import zapi
from Products.minaraad.subscriptions import SubscriptionManager, Subscription

from Products.Five.traversable import FakeRequest
from zope.app.publication.browser import setDefaultSkin



class testSubscriptions(MainTestCase):
    """ Test cases for the generic Subscriptions of the product
    """

    def afterSetUp(self):
        """ 
        """
        
        membership = self.portal.portal_membership
        membership.addMember('member', 'secret', ['Member'], [])
        
    def test_subscriptionManager(self):
        self.login('member')

        sm = SubscriptionManager(self.portal)

        for subscription in sm.subscriptions:
            self.failIf(subscription.email)
            self.failIf(subscription.post)

        sm.subscribe('Advisory', email=True, post=False)
        
        for subscription in sm.subscriptions:
            if subscription.id == 'Advisory':
                self.failUnless(subscription.email)
                self.failIf(subscription.post)
            else:
                self.failIf(subscription.email)
                self.failIf(subscription.post)

        subscriptions = sm.subscriptions
        id = subscriptions[1].id
        subscriptions[1].post = True
        sm.subscriptions = subscriptions
        
        for subscription in sm.subscriptions:
            if subscription.id == 'Advisory':
                self.failUnless(subscription.email)
                self.failIf(subscription.post)
            elif subscription.id == id:
                self.failIf(subscription.email)
                self.failUnless(subscription.post)
            else:
                self.failIf(subscription.email)
                self.failIf(subscription.post)
        
        self.logout()
        


    def test_browserSaveSubscriptions(self):
        self.login('member')

        sm = SubscriptionManager(self.portal)

        request = FakeRequest()
        setDefaultSkin(request)
        view = zapi.getView(self.portal, 
                            'subscriptions_config.html', 
                            request)

        request.form = {}
        for x in view.subscriptions():
            self.failIf(x['subscribed_post'])
            self.failIf(x['subscribed_email'])

        request['email_Advisory'] = 'yes' # string values here mean nothing
        request['email_Study'] = 'yes'
        view._saveSubscriptions()

        for x in sm.subscriptions:
            if x.id in ('Advisory', 'Study'):
                self.failUnless(x.email)
            else:
                self.failIf(x.email)
            self.failIf(x.post)

        self.logout()
        
    def test_browserSubscriptions(self):
        self.login('member')

        request = FakeRequest()
        setDefaultSkin(request)
        view = zapi.getView(self.portal, 
                            'subscriptions_config.html', 
                            request)

        sm = SubscriptionManager(self.portal)
        subscriptions = view.subscriptions()
        
        self.failUnless(len(sm.subscriptions) == len(subscriptions))
        
        subDict = {}
        for x in subscriptions:
            subDict[x['id']] = x

        for x in sm.subscriptions:
            self.failUnless(subDict.has_key(x.id))

        self.logout()


    def test_exportSubscribers(self):
        self.loginAsPortalOwner()
        self.portal.adviezen.adv_2006.invokeFactory('Advisory','myadvisory')
        advisory = self.portal.adviezen.adv_2006.myadvisory

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

        view = zapi.getView(advisory, 
                            'export_subscribers', 
                            request)

        HEADER_FIELDS = ("Aanhef","Voornaam","Achternaam","Organisatie",
                         "Functie","Straat","Huisnummer","Bus","Postcode",
                         "Woonplaats","Land","Ander land","Telefoonnummer",
                         "E-mail")
        headingLine = ''
        for x in HEADER_FIELDS:
            headingLine += '"%s",' % x
        headingLine = headingLine[:-1] + '\n'
        self.assertEquals(view(), headingLine)

        # let's do the actual subscription of our member
        sm.subscribe('Advisory', email=True, post=False)

        lines = view().split('\n')
        self.assertEquals(lines[1], '"Yes","John","Doe","Doe Enterprises",'
                          '"","Doe Street","23","Bus C","007",'
                          '"Rotterdam","The Netherlands","","",""')

        # let's make some assertions about the response
        self.assertEquals(
            request.response['content-type'],
            'application/vnd.ms-excel; charset=utf-8'
            )

        self.assertEquals(
            request.response['content-disposition'],
            'attachment; filename=advisory-subscribers.csv'
            )

        request['form.button.ExportEmail'] = None
        request['form.button.ExportPost'] = True
        
        view = zapi.getView(advisory, 
                            'export_subscribers', 
                            request)

        self.assertEquals(view(), headingLine)

    def test_getSelectedSubjects(self):
        self.setRoles('Manager')
        sm = SubscriptionManager(self.portal)
        request = FakeRequest()
        setDefaultSkin(request)
        request['SESSION'] = request.SESSION = {}
        view = zapi.getView(self.portal, 
                            'subscribers_config.html', 
                            request)
        # Overwrite the index, as we don't need to view the actual
        # html
        view.index = lambda **kw:None
        view()

        selectedSubjects = view.getSelectedSubjects()
        self.assertEqual(len(selectedSubjects), 0)

        request['category'] = 'Advisory'
        view()
        selectedSubjects = view.getSelectedSubjects()
        self.assertEqual(selectedSubjects, ['Advisory'])
        self.assertEqual(request.SESSION['category'], 'Advisory')

        request['category'] = 'Hearing'
        view()
        selectedSubjects = view.getSelectedSubjects()
        self.assertEqual(selectedSubjects, ['Hearing'])
        self.assertEqual(request.SESSION['category'], 'Hearing')

        request['theme'] = ['theme_1', 'theme_2']
        view()
        selectedSubjects = view.getSelectedSubjects()
        self.assertEqual(selectedSubjects, ['Hearing', 'theme_1', 'theme_2'])
        self.assertEqual(request.SESSION['category'], 'Hearing')
        self.assertEqual(request.SESSION['theme'], ['theme_1', 'theme_2'])

        request['category'] = 'Advisory'
        view()
        selectedSubjects = view.getSelectedSubjects()
        self.assertEqual(selectedSubjects, ['Advisory'])
        self.assertEqual(request.SESSION['category'], 'Advisory')
        self.assertEqual(request.SESSION['theme'], None)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testSubscriptions))
    return suite

if __name__ == '__main__':
    framework()


