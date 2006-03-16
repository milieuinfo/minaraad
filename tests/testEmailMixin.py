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

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

##code-section module-header #fill in your manual code here
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
##/code-section module-header

#
# Test-cases for class(es) EmailMixin
#

from Testing import ZopeTestCase
from Products.minaraad.config import *
from Products.PloneTestCase.PloneTestCase import PloneTestCase

# Import the tested classes
from Products.minaraad.EmailMixin import EmailMixin

##code-section module-beforeclass #fill in your manual code here
import email
from Products.Archetypes.atapi import registerType, BaseContent, BaseSchema
from Products.minaraad.subscriptions import SubscriptionManager
from Products.minaraad.EmailMixin import AlreadySentError, generateSafe
##/code-section module-beforeclass


class testEmailMixin(PloneTestCase):
    """Test-cases for class(es) EmailMixin."""

    ##code-section class-header_testEmailMixin #fill in your manual code here
    ##/code-section class-header_testEmailMixin

    def afterSetUp(self):
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = MockMailHost()
        self.portal.portal_membership.addMember('member', 'secret', 
                                                ['Member'], [], 
                                                {'email': 'someguy@hisplace.com'})
        self.portal.portal_membership.addMember('member2', 'secret', 
                                                ['Member'], [], 
                                                {'email': 'anotherguy@hisplace.com'})

    # from class EmailMixin:
    def test_email(self):
        self.login('member')

        emailMixin = MockEmailMixin('blah')
        emailMixin = emailMixin.__of__(self.portal)
        emailMixin.setTitle('Blah')

        emailMixin.email()
        
        mailHost = self.portal.MailHost
        self.assertEqual(len(mailHost.messages), 0)
        mailHost.reset()
        
        # lets test to make sure only-one-email-can-be-sent feature works
        self.failUnlessRaises(AlreadySentError, emailMixin.email)
        emailMixin.setEmailSent(None)

        # now lets test that unlimited test emails can be sent
        emailMixin.email(testing=True)
        emailMixin.email(testing=True)
        # and one real email
        emailMixin.email(text='extra')
        self.failUnlessRaises(AlreadySentError, emailMixin.email)
        emailMixin.setEmailSent(None)
        mailHost.reset()

        
        sm = SubscriptionManager(self.portal)
        sm.subscribe(MockEmailMixin.MOCK_NAME)
        
        # we want the mixin to be able to acquire a template
        template = ZopePageTemplate("some id")
        template.write("""
        <span tal:replace='context/Title' />
        <span tal:replace='member/email' />
        <a href="http://boo.com">hello</a>
        """)
        setattr(emailMixin, "EmailTemplate-Default", template)

        emailMixin.email()
        emailMixin.setEmailSent(None)
        self.assertEqual(len(mailHost.messages), 1)
        mailHost.reset()
        
        text = "Some random additional info"
        emailMixin.email(text, ('member2',))
        emailMixin.setEmailSent(None)
        msg = mailHost.messages[0]
        textParts = [x for x in msg.walk() 
                       if x.get('Content-Type','').find('text/plain') > -1]
        payload = textParts[0].get_payload(decode=True)
        self.failUnless(text in payload)
        self.failUnless('@hisplace.com' in payload)
        self.failUnless(emailMixin.Title() in payload)
        
        # make sure generateSafe() did its thing
        self.failUnless('hello (http://boo.com)' in payload)
        
        lst1 = [x['To'] for x in mailHost.messages]
        lst1.sort()
        
        self.assertEquals(lst1, ['anotherguy@hisplace.com', 'someguy@hisplace.com'])
        
        
        
        self.logout()
        
    # from class EmailMixin:
    def test_getEmailBody(self):
        pass

    # from class EmailMixin:
    def test_getSubscriptionId(self):
        pass

    # Manually created methods

    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        del self.portal._original_MailHost
    
    def test_generatingSafe(self):
        html = '<a href="http://blah.com">Some Blah</a>'

        result = generateSafe(html)
        self.assertEquals(result, '<a href="http://blah.com">Some Blah</a> (http://blah.com)')

    def test_getEmailContentsFromContent(self):
        pass

    def test_getEmailContents(self):
        pass

    def test_email_out(self):
        pass

    def test_subscribers_export(self):
        pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testEmailMixin))
    return suite

##code-section module-footer #fill in your manual code here
class MockEmailMixin(EmailMixin, BaseContent):
    """A mock class that extends EmailMixin.  Using this class is the only
    way to test with Archetypes auto-generated field accessors/mutators."""

    schema = BaseSchema + EmailMixin.schema
    
    MOCK_NAME = 'Advisory'
    
    def getSubscriptionId(self):
        return MockEmailMixin.MOCK_NAME

registerType(MockEmailMixin, PROJECTNAME)

class MockMailHost:
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.messages = []
    
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
        

##/code-section module-footer

if __name__ == '__main__':
    framework()


