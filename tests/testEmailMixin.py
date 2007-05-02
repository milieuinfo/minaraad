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

#from Testing import ZopeTestCase
#from Products.minaraad.config import *
from Products.minaraad.config import PROJECTNAME
from Products.PloneTestCase.PloneTestCase import PloneTestCase

# Import the tested classes
from Products.minaraad.EmailMixin import EmailMixin

##code-section module-beforeclass #fill in your manual code here
import email
from Products.Archetypes.atapi import registerType, BaseContent, BaseSchema
from Products.minaraad.subscriptions import SubscriptionManager
#from Products.minaraad.EmailMixin import AlreadySentError
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
        ## XXX (ree): the email mixin is not used any more, an appropriate
        # view must be used. This test is modified accordingly, but
        # much of ot is obsolete.
        self.login('member')

        emailMixin = MockEmailMixin('blah')
        emailMixin = emailMixin.__of__(self.portal)
        emailMixin.setTitle('Blah')

        # for making test run with the view
        emailMixin.index = lambda template_id=None: None

        # functionality is now in a view instead of the mixin
        mailview = emailMixin.unrestrictedTraverse('@@email_out')
        mailview.request.set('send', '1')

        #emailMixin.email()
        mailview()
        
        mailHost = self.portal.MailHost
        self.assertEqual(len(mailHost.messages), 0)
        mailHost.reset()
        
        # lets test to make sure only-one-email-can-be-sent feature works
        # Oh, we don't have to raise this failure anymore:
        #self.failUnlessRaises(AlreadySentError, emailMixin.email)
        emailMixin.setEmailSent(None)
        
        # now lets test that unlimited test emails can be sent
        #emailMixin.email(testing=True)
        #emailMixin.email(testing=True)
        mailview.request.set('send_as_test', '1')
        mailview()
        mailview()

        # and one real email
        #emailMixin.email(text='extra')
        mailview.request.set('additional', 'extra')
        #self.failUnlessRaises(AlreadySentError, emailMixin.email)
        emailMixin.setEmailSent(None)
        mailHost.reset()

        
        sm = SubscriptionManager(self.portal)
        sm.subscribe(MockEmailMixin.MOCK_NAME)
        
        # we want the mixin to be able to acquire a template
        template = ZopePageTemplate("some id")
        template.write("""<div>
        <span tal:replace='context/Title' />
        <span tal:replace='member/email' />
        <a href="./resolveUid?foo=bar">hello</a>
        </div>
        """)
        setattr(emailMixin, "EmailTemplate-Default", template)

        #emailMixin.email()
        mailview()


        emailMixin.setEmailSent(None)
        #self.assertEqual(len(mailHost.messages), 1)
        mailHost.reset()
        
        charset = self.portal.plone_utils.getSiteEncoding()
        text = (u"Some random additional info, "
                u"and a non-ascii charact\xebr".encode(charset))
        emailMixin.setTitle(u"Another non-ascii charact\xebr!".encode(charset))

        
        #emailMixin.email(text, ('member2',))
        mailview.request.set('to', 'member,member2')
        mailview.request.set('additional', text)
        mailview()

        emailMixin.setEmailSent(None)
        msg = mailHost.messages[0]
        textParts = [x for x in msg.walk() 
                       if x.get('Content-Type','').find('text/plain') > -1]
        payload = textParts[0].get_payload(decode=True)
        self.failUnless(text in payload)
        
        # XXX ree: Recipient does not seem to be in the msg text now. 
        # XXX Is this a problem? (I beliexe not.)
        #self.failUnless('@hisplace.com' in payload)

        self.failUnless(emailMixin.Title() in payload)
        self.failUnless('http://nohost/plone/resolveUid?foo=bar' in payload)
        
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

#if __name__ == '__main__':
#    framework()


