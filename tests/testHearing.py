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

    # from class Hearing:
    def test_getThemesList(self):
        pass

    # from class Hearing:
    def test_getThemeName(self):
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
    def test_themeslist(self):
        """ Test the theme list function in the Hearing content type
        """

        themes = self.hoorzitting.getThemesList()
        self.failUnless(len(themes)>0)

    def test_Fields(self):
        """ Test if the Hearing has all the required fields
        """

        self.hoorzitting.Title()          # Titel
        self.hoorzitting.getDescription() # Omschrijving
        self.hoorzitting.getGoal()        # Doelstelling
        self.hoorzitting.getSubheader     # Subkop
        self.hoorzitting.getLocation      # Lokatie
        self.hoorzitting.getStartdate     # Start tijd
        self.hoorzitting.getEnddate       # Eind tijd
        self.hoorzitting.getTheme         # Thema's
        self.hoorzitting.getBody          # Body
        self.hoorzitting.getPlaintext     # Platte tekst
        self.hoorzitting.getContact       # Contactpersoon


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testHearing))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


