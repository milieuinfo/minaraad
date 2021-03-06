# -*- coding: utf-8 -*-
#
# File: testContactPerson.py
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


class testContactPerson(MainTestCase):
    """ test-cases for class(es) ContactPerson
    """

    def afterSetUp(self):
        """ Initialization of user and ContactPerson
        """

        self.portal.portal_membership.addMember(
            'manager', 'secret', ['Manager'], [])
        self.login('manager')

        self.portal.contactpersonen.invokeFactory('ContactPerson',
                                                  'mycontactperson')
        self.contactperson = self.portal.contactpersonen.mycontactperson

    def test_Fields(self):

        self.contactperson.getName()         # Naam
        self.contactperson.getJobtitle()     # Functie
        self.contactperson.getDepartment()   # Afdeling
        self.contactperson.getEmail()        # E-mailadres
        self.contactperson.getPhonenumber()  # Telefoonnummer

    def test_Existance(self):
        """ Test if the ContactPerson exists within portal_types
        """

        types_ = self.portal.portal_types.objectIds()
        self.failUnless('ContactPerson' in types_)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testContactPerson))
    return suite
