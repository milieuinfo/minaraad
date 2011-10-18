# -*- coding: utf-8 -*-
#
# File: testNewsLetter.py
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

from DateTime import DateTime

from Products.minaraad.tests.MainTestCase import MainTestCase


TITLE = "title"
DESCRIPTION = "my description"
DATE = DateTime()
HTMLBODY = "<p>blablabla blablabla bladibladi bla</p>"
PLAINBODY = "blablabla blablabla bladibladi bla"


class testNewsLetter(MainTestCase):
    """ test-cases for class(es) NewsLetter
    """

    def afterSetUp(self):
        """
        """

        self.setRoles(['Manager'])
        self.portal.nieuwsbrieven.newsl_2006.invokeFactory('NewsLetter',
                                                           id='testnewsletter')
        self.testnewsletter = \
            self.portal.nieuwsbrieven.newsl_2006.testnewsletter

        self.portal.contactpersonen.invokeFactory('ContactPerson', id='Joris')
        self.contactperson = self.portal.contactpersonen.Joris

    def testNewsLetter(self):
        """ Test if the Newsletter is in the portal_types
        """
        types_ = self.portal.portal_types.objectIds()
        self.failUnless('NewsLetter' in types_)

    def testProperties(self):
        """ Test if the Newsletter has the correct properties
        """

        self.testnewsletter.setTitle(TITLE)
        self.testnewsletter.setDescription(DESCRIPTION)
        self.testnewsletter.setDate(DATE)
        self.testnewsletter.setBody(HTMLBODY, text_format="text/html")

        self.failUnless(self.testnewsletter.Title()==TITLE,
                        'Value is %s' % self.testnewsletter.Title())
        self.failUnless(self.testnewsletter.getDescription()==DESCRIPTION,
                        'Value is %s' % self.testnewsletter.getDescription())
        self.failUnless(self.testnewsletter.getDate()==DATE,
                        'Value is %s' % self.testnewsletter.getDate())
        self.failUnless(self.testnewsletter.getBody()==HTMLBODY,
                        'Value %s is not %s' % (self.testnewsletter.getBody(),
                                                HTMLBODY))

        self.testnewsletter.setBody(PLAINBODY, text_format="text/plain")
        self.failUnless(self.testnewsletter.getBody()==HTMLBODY,
                        'Value %s is not %s' % (self.testnewsletter.getBody(),
                                                HTMLBODY))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testNewsLetter))
    return suite
