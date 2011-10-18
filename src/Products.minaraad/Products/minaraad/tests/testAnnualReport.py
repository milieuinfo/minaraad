# -*- coding: utf-8 -*-
#
# File: testAnnualReport.py
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

from Products.minaraad.tests.utils import load_file

TITLE = "title"
ATTACHMENT = load_file('test.pdf')


class testAnnualReport(MainTestCase):
    """ test-cases for class(es) AnnualReport
    """

    def afterSetUp(self):
        """
        """
        self.setRoles(['Manager'])
        self.portal.jaarverslag.invokeFactory('AnnualReport',
                                              id='testar')
        self.testar = self.portal.jaarverslag.testar

    def testAnnualReport(self):
        """ Test if the AnnualReport is in the portal_types
        """
        types_ = self.portal.portal_types.objectIds()
        self.failUnless('AnnualReport' in types_)

    def testProperties(self):
        """ Test if the AnnualReport has the correct properties
        """

        self.testar.setTitle(TITLE)
        self.testar.setAttachment(ATTACHMENT, content_type="application/pdf")

        self.failUnless(self.testar.Title()==TITLE,
                         'Value is %s' % self.testar.Title())
        myclass = str(self.testar.getAttachment().__class__)
        correct = "<class 'OFS.Image.File'>"
        self.failUnless(myclass==correct, 'Value is %s and not %s' %
                        (myclass, correct))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testAnnualReport))
    return suite
