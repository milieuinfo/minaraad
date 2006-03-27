# -*- coding: utf-8 -*-
#
# File: testStudy.py
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
# Test-cases for class(es) Study
#

from Testing import ZopeTestCase
from Products.minaraad.config import *
from Products.minaraad.tests.MainTestCase import MainTestCase

# Import the tested classes
from Products.minaraad.content.Study import Study

##code-section module-beforeclass #fill in your manual code here
from DateTime import DateTime

TITLE = "title"
SUBHEADER = "ondertitel"
DESCRIPTION = "een omschrijving"
LOCATION = "een plaats"
STARTDATE = DateTime()
ENDDATE = DateTime()
SPEAKERS = ("Joris","Slob")
HTMLBODY = "<p>HTML Body boodschap</p>"

##/code-section module-beforeclass


class testStudy(MainTestCase):
    """ test-cases for class(es) Study
    """

    ##code-section class-header_testStudy #fill in your manual code here
    ##/code-section class-header_testStudy

    def afterSetUp(self):
        """
        """
        self.setRoles(['Manager'])
        self.portal.studies.invokeFactory('Study',id='teststudy')
        self.teststudy = self.portal.studies.teststudy

        self.portal.contactpersonen.invokeFactory('ContactPerson', id='Jslob')
        self.contactperson = self.portal.contactpersonen.Jslob

        pass
    # from class Study:
    # from class Study:
    def test_email_out(self):
        pass

    # from class Study:
    def test_export_subscribers(self):
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

    def test_getEmailContentsFromContent(self):
        pass

    def testStudy(self):
        """ Test if the Study is in the portal_types
        """
        types_ = self.portal.portal_types.objectIds()
        self.failUnless('Study' in types_)

    def test_getEmailContents(self):
        pass

    def test_subscribers_export(self):
        pass

    def testProperties(self):
        """ Test if the Study has the correct properties
        """

        self.teststudy.setTitle(TITLE)
        self.teststudy.setSubheader(SUBHEADER)
        self.teststudy.setDescription(DESCRIPTION)
        self.teststudy.setLocation(LOCATION)
        self.teststudy.setStartdate(STARTDATE)
        self.teststudy.setEnddate(ENDDATE)
        self.teststudy.setSpeakers(SPEAKERS)
        self.teststudy.setBody(HTMLBODY,text_format="text/html")
        self.teststudy.setContact(self.contactperson.UID())

        self.failUnless(self.teststudy.Title()==TITLE,
                         'Value is %s' % self.teststudy.Title())
        self.failUnless(self.teststudy.getSubheader()==SUBHEADER,
                         'Value is %s' % self.teststudy.getSubheader())
        self.failUnless(self.teststudy.getDescription()==DESCRIPTION,
                         'Value is %s' % self.teststudy.getDescription())
        self.failUnless(self.teststudy.getLocation()==LOCATION,
                         'Value is %s' % self.teststudy.getLocation())
        self.failUnless(self.teststudy.getStartdate()==STARTDATE,
                         'Value is %s' % self.teststudy.getStartdate())
        self.failUnless(self.teststudy.getEnddate()==ENDDATE,
                         'Value is %s' % self.teststudy.getEnddate())
        self.failUnless(self.teststudy.getSpeakers()==SPEAKERS,
                         'Value is %s' % str(self.teststudy.getSpeakers()))
        self.failUnless(self.teststudy.getBody()==HTMLBODY,
                         'Value is %s' % self.teststudy.getBody())
        self.failUnless(self.teststudy.getContact()==[self.contactperson],
                         'Value is %s' % self.teststudy.getContact())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testStudy))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


