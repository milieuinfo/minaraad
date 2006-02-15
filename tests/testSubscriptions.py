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
from Products.Five.traversable import FakeRequest

class testSubscriptions(MainTestCase):
    """ Test cases for the generic Subscriptions of the product
    """

    def afterSetUp(self):
        """ 
        """
        
        membership = self.portal.portal_membership
        membership.addMember('member', 'secret', ['Member'], [])
        

    def test_configletView(self):
        self.login('member')


        request = FakeRequest()
        view = zapi.getView(self.portal, 
                            'subscriptions_config.html', 
                            request)

        request.form = {}
        for x in view.subscriptions():
            self.failIf(x['subscribed_post'])
            self.failIf(x['subscribed_email'])

        request.form['email_Advisory'] = True
        request.form['email_Study'] = True
        view._saveSubscriptions()

        for x in view.subscriptions():
            if x['id'] in ('Advisory', 'Study'):
                self.failUnless(x['subscribed_email'])
            else:
                self.failIf(x['subscribed_email'])
            self.failIf(x['subscribed_post'])

        self.logout()
        
        



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testSubscriptions))
    return suite

if __name__ == '__main__':
    framework()


