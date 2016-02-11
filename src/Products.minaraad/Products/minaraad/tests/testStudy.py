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


from Products.minaraad.tests.MainTestCase import MainTestCase

from DateTime import DateTime

TITLE = "title"
SUBHEADER = "ondertitel"
DESCRIPTION = "een omschrijving"
LOCATION = "een plaats"
DATE = DateTime()
SPEAKERS = ("Joris", "Slob")
HTMLBODY = "<p>HTML Body boodschap</p>"


class testStudy(MainTestCase):
    """ test-cases for class(es) Study
    """

    def afterSetUp(self):
        """
        """
        self.setRoles(['Manager'])
        self.portal.studies.invokeFactory('Study', id='teststudy')
        self.teststudy = self.portal.studies.teststudy

        self.portal.contactpersonen.invokeFactory('ContactPerson', id='Jslob')
        self.contactperson = self.portal.contactpersonen.Jslob

    def testStudy(self):
        """ Test if the Study is in the portal_types
        """
        types_ = self.portal.portal_types.objectIds()
        self.failUnless('Study' in types_)

    def testProperties(self):
        """ Test if the Study has the correct properties
        """

        self.teststudy.setTitle(TITLE)
        self.teststudy.setDescription(DESCRIPTION)
        self.teststudy.setDate(DATE)
        self.teststudy.setContact(self.contactperson.UID())

        self.failUnless(self.teststudy.Title() == TITLE,
                        'Value is %s' % self.teststudy.Title())
        self.failUnless(self.teststudy.getDescription() == DESCRIPTION,
                        'Value is %s' % self.teststudy.getDescription())
        self.failUnless(self.teststudy.getDate() == DATE,
                        'Value is %s' % self.teststudy.getDate())
        self.failUnless(self.teststudy.getContact() == [self.contactperson],
                        'Value is %s' % self.teststudy.getContact())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testStudy))
    return suite
