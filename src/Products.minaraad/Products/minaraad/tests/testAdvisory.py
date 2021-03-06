# -*- coding: utf-8 -*-
#
# File: testAdvisory.py
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
DESCRIPTION = "kijk altijd naar beide kanten voor het oversteken"
DATE = DateTime()
HTMLBODY = "<p>HTML op zijn best</p>"


class testAdvisory(MainTestCase):
    """ test-cases for class(es) Advisory
    """

    def afterSetUp(self):
        """ Initialization of user and Advisory
        """

        self.portal.portal_membership.addMember(
            'manager', 'secret', ['Manager'], [])
        self.login('manager')

        self.portal.adviezen.adv_2006.invokeFactory(
            'Advisory', 'myadvisory')
        self.advisory = self.portal.adviezen.adv_2006.myadvisory

        self.portal.contactpersonen.invokeFactory('ContactPerson', id='Jslob')
        self.contactperson = self.portal.contactpersonen.Jslob

    def test_Fields(self):
        """ Test if the Advisory has all the required fields
        """

        self.advisory.setTitle(TITLE)
        self.advisory.setDescription(DESCRIPTION)
        self.advisory.setDate(DATE)
        self.advisory.setContact(self.contactperson.UID())
        self.advisory.setBody(HTMLBODY, text_format="text/html")

        self.failUnless(self.advisory.Title() == TITLE,
                        'Value is %s' % self.advisory.Title())
        self.failUnless(self.advisory.getDescription() == DESCRIPTION,
                        'Value is %s' % self.advisory.getDescription())
        self.failUnless(self.advisory.getDate() == DATE,
                        'Value is %s' % self.advisory.getDate())
        self.failUnless(self.advisory.getContact() == [self.contactperson],
                        'Value is %s' % self.advisory.getContact())
        self.failUnless(self.advisory.getBody() == HTMLBODY,
                        'Value is %s' % self.advisory.getBody())

    def test_Existance(self):
        """ Test if the Advisory exists within portal_types
        """

        types_ = self.portal.portal_types.objectIds()
        self.failUnless('Advisory' in types_)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testAdvisory))
    return suite
