# -*- coding: utf-8 -*-
#
# File: testPressrelease.py
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
# Test-cases for class(es) Pressrelease
#

from Testing import ZopeTestCase
from Products.minaraad.config import *
from Products.minaraad.tests.MainTestCase import MainTestCase

# Import the tested classes
from Products.minaraad.content.Pressrelease import Pressrelease

##code-section module-beforeclass #fill in your manual code here
from DateTime import DateTime

TITLE = "title"
SUBHEADER = "ondertitel"
DESCRIPTION = "jaja, een omschrijving"
DATE = DateTime()
HTMLBODY = "<p>HTML op zijn best</p>"
PLAINBODY = "HTML op zijn best"

##/code-section module-beforeclass


class testPressrelease(MainTestCase):
    """ test-cases for class(es) Pressrelease
    """

    ##code-section class-header_testPressrelease #fill in your manual code here
    ##/code-section class-header_testPressrelease

    def afterSetUp(self):
        """
        """

        self.setRoles(['Manager'])
        self.portal.persberichten.pressr_2006.invokeFactory('Pressrelease',id='testpers')
        self.testpers = self.portal.persberichten.pressr_2006.testpers

        self.portal.contactpersonen.invokeFactory('ContactPerson', id='Jslob')
        self.contactperson = self.portal.contactpersonen.Jslob

    # from class Pressrelease:
    def test_email_out(self):
        pass

    # from class EmailMixin:
    def test_email(self):
        """
        """
        #Uncomment one of the following lines as needed
    # from class EmailMixin:
    def test_getEmailBody(self):
        pass

    # from class EmailMixin:
    def test_getSubscriptionId(self):
        pass

    # Manually created methods

    def testPressrelease(self):
        """ Test if the Pressrelease is in the portal_types
        """
        types_ = self.portal.portal_types.objectIds()
        self.failUnless('Pressrelease' in types_)

    def test_getEmailContentsFromContent(self):
        pass

    def test_getEmailContents(self):
        pass

    def test_subscribers_export(self):
        pass

    def testProperties(self):
        """ Test if the Pressrelease has the correct properties
        """

        self.testpers.setTitle(TITLE)
        self.testpers.setSubheader(SUBHEADER)
        self.testpers.setDescription(DESCRIPTION)
        self.testpers.setDate(DATE)
        self.testpers.setBody(HTMLBODY,text_format="text/html")
        self.testpers.setContact(self.contactperson.UID())

        self.failUnless(self.testpers.Title()==TITLE,
                         'Value is %s' % self.testpers.Title())
        self.failUnless(self.testpers.getSubheader()==SUBHEADER,
                         'Value is %s' % self.testpers.getSubheader())
        self.failUnless(self.testpers.getDescription()==DESCRIPTION,
                         'Value is %s' % self.testpers.getDescription())
        self.failUnless(self.testpers.getDate()==DATE,
                         'Value is %s' % self.testpers.getDate())
        self.failUnless(self.testpers.getBody()==HTMLBODY,
                         'Value is %s' % self.testpers.getBody())
        self.failUnless(self.testpers.getContact()==[self.contactperson],
                         'Value is %s' % self.testpers.getContact())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testPressrelease))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


