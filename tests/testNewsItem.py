# -*- coding: utf-8 -*-
#
# File: testNewsItem.py
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
# Test-cases for class(es) NewsItem
#

from Testing import ZopeTestCase
from Products.minaraad.config import *
from Products.minaraad.tests.MainTestCase import MainTestCase

# Import the tested classes
from Products.minaraad.content.NewsItem import NewsItem

##code-section module-beforeclass #fill in your manual code here
##/code-section module-beforeclass


class testNewsItem(MainTestCase):
    """Test-cases for class(es) NewsItem."""

    ##code-section class-header_testNewsItem #fill in your manual code here
    ##/code-section class-header_testNewsItem

    def afterSetUp(self):
        pass

    # from class EmailMixin:
    def test_email(self):
        pass

    # from class EmailMixin:
    def test_getEmailBody(self):
        pass

    # from class EmailMixin:
    def test_getSubscriptionId(self):
        pass

    # from class EmailMixin:
    def test_getEmailContentsFromContent(self):
        pass

    # Manually created methods
    def testNewsItem(self):
        """ Test to see if NewsItem is in the portal_types
        """

        types_ = self.portal.portal_types.objectIds()
        self.failUnless('NewsItem' in types_)

    def testProperties(self):
        """ Test if the Newsletter has the correct properties
        """

        self.setRoles(['Manager'])
        self.portal.nieuwsbrieven.newsl_2006.invokeFactory('NewsLetter', id='testnewsletter2')
        self.portal.nieuwsbrieven.newsl_2006.testnewsletter2.invokeFactory('NewsItem', id='testnewsitem')
        testnewsitem = self.portal.nieuwsbrieven.newsl_2006.testnewsletter2.testnewsitem

        testnewsitem.setTitle("Do I have a Title?")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testNewsItem))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


