__author__ = """Daniel Nouri <d.nouri@zestsoftware.nl>"""
__docformat__ = 'plaintext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

#
# Test-cases for class(es)
#

from Testing import ZopeTestCase
from Products.PloneTestCase.PloneTestCase import PloneTestCase

from Products.minaraad.config import *
from Products.minaraad.utils import member
import Products.minaraad.tests.MainTestCase
import email

class testUtilsMember(PloneTestCase):

    def afterSetUp(self):
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = MockMailHost()
        self.portal.portal_membership.addMember(
            'member', 'secret',
            ['Member'], [], {'email': 'someguy@hisplace.com',
                             'fullname': 'Member',
                             'firstname': 'First',
                             })
        
        self.portal.portal_membership.addMember(
            'member2', 'secret',
            ['Member'], [], {'email': '',
                             'fullname': 'Member',
                             'firstname': 'Second',
                             })

        self.portal.portal_membership.addMember(
            'member3', '3re',
            ['Member'], [], {'email': 'automatedguy@zestsoftware.uk',
                             'fullname': 'Member',
                             'firstname': 'Third',
                             })

    def test_getAllMembers(self):
        members = member.getAllMembersWithThreeLetterPassword(self.portal)
        self.assertEquals(len(members), 1)
        self.assertEquals(members[0].id, 'member3')

    def test_getAllMembersWithEmail(self):
        members = member.getAllMembersWithEmail(self.portal)
        self.assertEquals(len(members), 1)
        self.assertEquals(members[0].id, 'member3')

    def test_sendEmailForAllMembersWithEmail(self):
        member.sendEmailForAllMembersWithEmail(self.portal)
        mailhost = self.portal.MailHost
        # XXX Continue here
        import pdb; pdb.set_trace()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testUtilsMember))
    return suite

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


if __name__ == '__main__':
    framework()


