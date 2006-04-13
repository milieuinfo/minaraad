# -*- coding: utf-8 -*-
#
# File: testHearing.py
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
# Test-cases for class(es) Hearing
#

from Testing import ZopeTestCase
from Products.minaraad.config import *
from Products.minaraad.tests.MainTestCase import MainTestCase

# Import the tested classes
from Products.minaraad.content.Hearing import Hearing

##code-section module-beforeclass #fill in your manual code here
from DateTime import DateTime
from Products.minaraad.tests.utils import load_file

TITLE = "title"
SUBHEADER = "ondertitel"
DESCRIPTION = "jaja, een ondertitel"
GOAL = "Doel"
LOCATION = "Hoogvliet"
THEME = 0
MOT = bool(1)
STARTDATE = DateTime()
ENDDATE = DateTime()
HTMLBODY = "<p>HTML op zijn best</p>"
TESTIMAGE = load_file('test.gif')

##/code-section module-beforeclass


class testHearing(MainTestCase):
    """ test-cases for class(es) Hearing
    """

    ##code-section class-header_testHearing #fill in your manual code here
    ##/code-section class-header_testHearing

    def afterSetUp(self):
        """ Initialization of user and Hearing
        """
        self.portal.portal_membership.addMember('manager','secret',['Manager'],[])
        self.login('manager')

        self.portal.hoorzittingen.invokeFactory('Hearing','myhoorzitting')
        self.hoorzitting = self.portal.hoorzittingen.myhoorzitting

        self.portal.contactpersonen.invokeFactory('ContactPerson', id='Jslob')
        self.contactperson = self.portal.contactpersonen.Jslob

    # from class Hearing:
    def test_getThemesList(self):
        pass

    # from class Hearing:
    def test_getThemeName(self):
        pass

    # from class Hearing:
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

    def test_Existance(self):
        """ Test if the Hearing exists within portal_types
        """
        types_ = self.portal.portal_types.objectIds()
        self.failUnless('Hearing' in types_)

    def test_getThemes(self):
        """
        """
        #Uncomment one of the following lines as needed
    def test_getEmailContentsFromContent(self):
        pass

    def test_getEmailContents(self):
        pass

    def test_themeslist(self):
        """ Test the theme list function in the Hearing content type
        """

        themes = self.hoorzitting.getThemesList()
        self.failUnless(len(themes)>0)

    def test_Fields(self):
        """ Test if the Hearing has all the required fields
        """

        self.hoorzitting.setTitle(TITLE)
        self.hoorzitting.setDescription(DESCRIPTION)
        self.hoorzitting.setGoal(GOAL)
        self.hoorzitting.setSubheader(SUBHEADER)
        self.hoorzitting.setLocation(LOCATION)
        self.hoorzitting.setStartdate(STARTDATE)
        self.hoorzitting.setEnddate(ENDDATE)
        self.hoorzitting.setTheme(THEME)
        self.hoorzitting.setMot(MOT)
        self.hoorzitting.setContact(self.contactperson.UID())
        self.hoorzitting.setBody(HTMLBODY,text_format="text/html")
        self.hoorzitting.setFoto(TESTIMAGE, content_type="image/gif")

        self.failUnless(self.hoorzitting.Title()==TITLE,
                         'Value is %s' % self.hoorzitting.Title())
        self.failUnless(self.hoorzitting.getSubheader()==SUBHEADER,
                         'Value is %s' % self.hoorzitting.getSubheader())
        self.failUnless(self.hoorzitting.getDescription()==DESCRIPTION,
                         'Value is %s' % self.hoorzitting.getDescription())
        self.failUnless(self.hoorzitting.getGoal()==GOAL,
                         'Value is %s' % self.hoorzitting.getGoal())
        self.failUnless(self.hoorzitting.getLocation()==LOCATION,
                         'Value is %s' % self.hoorzitting.getLocation())
        self.failUnless(self.hoorzitting.getStartdate()==STARTDATE,
                         'Value is %s' % self.hoorzitting.getStartdate())
        self.failUnless(self.hoorzitting.getEnddate()==ENDDATE,
                         'Value is %s' % self.hoorzitting.getEnddate())
        self.failUnless(self.hoorzitting.getTheme()==THEME,
                         'Value is %s' % self.hoorzitting.getTheme())
        self.failUnless(self.hoorzitting.getMot()==MOT,
                         'Value is %s' % self.hoorzitting.getMot())
        self.failUnless(self.hoorzitting.getBody()==HTMLBODY,
                         'Value is %s' % self.hoorzitting.getBody())
        self.failUnless(self.hoorzitting.getContact()==[self.contactperson],
                         'Value is %s' % self.hoorzitting.getContact())
        myclass = str(self.hoorzitting.getFoto().__class__)
        correct = "<class 'Products.Archetypes.Field.Image'>"
        self.failUnless(myclass==correct, 'Value is %s and not %s' % (myclass,correct))

    def test_subscribers_export(self):
        pass

    def test_attendees(self):
        pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testHearing))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()
