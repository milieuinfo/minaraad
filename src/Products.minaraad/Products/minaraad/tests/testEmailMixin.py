# -*- coding: utf-8 -*-
#
# File: testEmailMixin.py
#
# Copyright (c) 2006 by Zest Software
# Generator: ArchGenXML Version 1.5.0 svn/devel
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

from Products.minaraad.tests.MainTestCase import MainTestCase


import email
import transaction

from Products.minaraad.subscriptions import SubscriptionManager


def mock_commit():
    """ We have to patch transaction.commit for those tests, otherwise
    we do not get emails in the MailHost.
    """
    pass


class testEmailMixin(MainTestCase):
    """Test-cases for class(es) EmailMixin."""

    def afterSetUp(self):
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = MockMailHost()
        from Products.MailHost.interfaces import IMailHost
        sm = self.portal.getSiteManager()
        sm.registerUtility(self.portal.MailHost, provided=IMailHost)

        self.portal.portal_membership.addMember(
            'bilbo', 'secret',
            ['Member'], [],
            {'email': 'bilbo@example.com',
             'firstname': 'Bilbo',
             'fullname': 'Baggins'})
        self.portal.portal_membership.addMember(
            'frodo', 'secret',
            ['Member'], [],
            {'email': 'frodo@example.com',
             'firstname': 'Frodo',
             'fullname': 'Baggins'})

    def test_email(self):
        # Some of this may be obsolete.
        self.loginAsPortalOwner()
        self.portal.jaarverslag.invokeFactory('AnnualReport', 'report')
        context = self.portal.jaarverslag.report

        transaction._old_commit = transaction.commit
        transaction.commit = mock_commit

        mailview = context.unrestrictedTraverse('@@email_out')
        # Only POST requests can really send mails.
        mailview.request['REQUEST_METHOD'] = 'POST'
        mailview.request.set('send', '1')

        # Can we render this?
        mailview()

        mailHost = self.portal.MailHost
        self.assertEqual(len(mailHost.messages), 0)
        mailHost.reset()

        # now lets test that test emails can be sent
        mailview.request.set('send_as_test', '1')
        mailview()
        mailview()

        # and one real email
        mailview.request.set('additional', 'extra')
        mailHost.reset()

        sm = SubscriptionManager(self.portal)
        sm.subscribe('AnnualReport')
        mailview()
        mailHost.reset()

        charset = self.portal.plone_utils.getSiteEncoding()
        text = (u"Some random additional info, "
                u"and a non-ascii charact\xebr".encode(charset))
        context.setTitle(u"Another non-ascii charact\xebr!".encode(charset))

        mailview.request.set('to', 'bilbo,frodo')
        mailview.request.set('additional', text)
        mailview()

        msg = mailHost.messages[0]
        textParts = [x for x in msg.walk()
                     if x.get('Content-Type', '').find('text/plain') > -1]
        payload = textParts[0].get_payload(decode=True)
        self.failUnless(text in payload, "Text not found in payload.")

        self.failUnless(context.Title() in payload,
                        "Context title not in payload.")
        self.failUnless('http://nohost/plone/jaarverslag/report' in payload,
                        "Context url not in payload.")
        self.failUnless("Bilbo" in payload,
                        "First name of member not in payload.")

        lst1 = [x['To'] for x in mailHost.messages]
        lst1.sort()

        self.assertEquals(lst1, ['bilbo@example.com',
                                 'frodo@example.com'])

        transaction.commit = transaction._old_commit

    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        del self.portal._original_MailHost


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testEmailMixin))
    return suite


class MockMailHost:

    def __init__(self):
        self.reset()

    def reset(self):
        self.messages = []

    def getId(self):
        return 'MailHost'

    def send(self, message, mto=None, mfrom=None, subject=None,
             encode=None):
        """
        Basically construct an email.Message from the given params to make sure
        everything is ok and store the results in the messages instance var.
        """

        message = email.message_from_string(message)
        message['To'] = mto
        message['From'] = mfrom
        message['Subject'] = subject

        self.messages.append(message)
