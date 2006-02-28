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

    # from class EmailMixin:
    def test_email(self):
        self.login('member')

        emailMixin = MockEmailMixin('blah')
        emailMixin = emailMixin.__of__(self.portal)
        emailMixin.setTitle('Blah')
        emailMixin.setEmailTemplate('<p><span tal:replace="context/Title"/></p>')

        emailMixin.email()
        
        mailHost = self.portal.MailHost
        self.assertEqual(len(mailHost.messages), 0)
        mailHost.reset()
        
        sm = SubscriptionManager(self.portal)
        sm.subscribe(MockEmailMixin.MOCK_NAME)
        emailMixin.email()
        self.assertEqual(len(mailHost.messages), 1)
        mailHost.reset()
        
        emailMixin.setEmailTemplate('<p><span tal:replace="options/emailText"/></p>')
        text = "Some random additional info"
        emailMixin.email(text, ['email@someotherguy'])
        msg = mailHost.messages[0]
        textParts = [x for x in msg.walk() 
                       if x.get('Content-Type','').find('text/plain') > -1]
        payload = textParts[0].get_payload(decode=True)
        self.failUnless(text in payload)
        
        lst1 = [x['To'] for x in mailHost.messages]
        lst1.sort()
        
        self.assertEquals(lst1, ['email@someotherguy', 'someguy@hisplace.com'])
        
        self.logout()
        
    # from class EmailMixin:
    def test_getEmailBody(self):
        emailMixin = MockEmailMixin('blah')
        emailMixin = emailMixin.__of__(self.portal)
        emailMixin.setTitle('Blah')
        emailMixin.setEmailTemplate('<p><span tal:replace="context/Title"/></p>')
        
        email = emailMixin.getEmailBody()
        self.assertEquals(str(email['text/html']).strip(), '<p>Blah</p>')
        self.assertEquals(str(email['text/plain']).strip(), 'Blah')
        
    # from class EmailMixin:
    def test_getSubscriptionId(self):
        pass

    # Manually created methods

    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        del self.portal._original_MailHost
    

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


