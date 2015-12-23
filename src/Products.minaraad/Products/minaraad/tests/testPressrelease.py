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

from Products.minaraad.tests.MainTestCase import MainTestCase

from DateTime import DateTime
from Products.minaraad.tests.utils import load_file

TITLE = "title"
SUBHEADER = "ondertitel"
DESCRIPTION = "jaja, een omschrijving"
DATE = DateTime()
HTMLBODY = "<p>HTML op zijn best</p>"
PLAINBODY = "HTML op zijn best"
TESTIMAGE = load_file('test.gif')


class testPressrelease(MainTestCase):
    """ test-cases for class(es) Pressrelease
    """

    def afterSetUp(self):
        """
        """

        self.setRoles(['Manager'])
        self.portal.persberichten.pressr_2006.invokeFactory('Pressrelease',
                                                            id='testpers')
        self.testpers = self.portal.persberichten.pressr_2006.testpers

        self.portal.contactpersonen.invokeFactory('ContactPerson', id='Jslob')
        self.contactperson = self.portal.contactpersonen.Jslob

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
        self.testpers.setBody(HTMLBODY, text_format="text/html")
        self.testpers.setContact(self.contactperson.UID())
        self.testpers.setLogo_1(TESTIMAGE, content_type="image/gif")
        self.testpers.setLogo_2(TESTIMAGE, content_type="image/gif")
        self.testpers.setFoto(TESTIMAGE, content_type="image/gif")

        self.failUnless(self.testpers.Title() == TITLE,
                        'Value is %s' % self.testpers.Title())
        self.failUnless(self.testpers.getSubheader() == SUBHEADER,
                        'Value is %s' % self.testpers.getSubheader())
        self.failUnless(self.testpers.getDescription() == DESCRIPTION,
                        'Value is %s' % self.testpers.getDescription())
        self.failUnless(self.testpers.getDate() == DATE,
                        'Value is %s' % self.testpers.getDate())
        self.failUnless(self.testpers.getBody() == HTMLBODY,
                        'Value is %s' % self.testpers.getBody())
        self.failUnless(self.testpers.getContact() == [self.contactperson],
                        'Value is %s' % self.testpers.getContact())
        myclass = str(self.testpers.getLogo_1().__class__)
        correct = "<class 'plone.app.blob.field.BlobWrapper'>"
        self.failUnless(myclass == correct, 'Value is %s and not %s' %
                        (myclass, correct))
        myclass = str(self.testpers.getLogo_2().__class__)
        self.failUnless(myclass == correct, 'Value is %s and not %s' %
                        (myclass, correct))
        myclass = str(self.testpers.getFoto().__class__)
        self.failUnless(myclass == correct, 'Value is %s and not %s' %
                        (myclass, correct))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testPressrelease))
    return suite
