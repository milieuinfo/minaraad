# -*- coding: utf-8 -*-
#
# File: testMREvent.py
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

TESTIMAGE = load_file('test.gif')


class testMREvent(MainTestCase):
    """ test-cases for class(es) MREvent
    """

    def afterSetUp(self):
        """ Initialization of user and MREvent
        """
        self.portal.portal_membership.addMember(
            'manager', 'secret', ['Manager'], [])
        self.login('manager')

        self.portal.evenementen.invokeFactory('MREvent', 'mymrevent')
        self.mrevent = self.portal.evenementen.mymrevent

    def test_Fields(self):
        """ Test if the MREvent has all the required fields
        """

        self.mrevent.Title()           # Titel
        self.mrevent.getDescription()  # Omschrijving
        self.mrevent.getGoal()         # Doelstelling
        self.mrevent.getSubheader()    # Subkop
        self.mrevent.getLocation()     # Lokatie
        self.mrevent.getStart_time()   # Start tijd
        self.mrevent.get_end_time()    # Eind tijd
        self.mrevent.getContact()      # Contactpersoon

        self.mrevent.setFoto(TESTIMAGE, content_type="image/gif")

        myclass = str(self.mrevent.getFoto().__class__)
        correct = "<class 'plone.app.blob.field.BlobWrapper'>"
        self.failUnless(myclass==correct, 'Value is %s and not %s' %
                        (myclass, correct))

    def test_Existance(self):
        """ Test if the MREvent exists within portal_types
        """

        types_ = self.portal.portal_types.objectIds()
        self.failUnless('MREvent' in types_)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testMREvent))
    return suite
