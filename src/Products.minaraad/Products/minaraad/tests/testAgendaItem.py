# -*- coding: utf-8 -*-
#
# File: testAgendaItem.py
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


class testAgendaItem(MainTestCase):
    """Test-cases for class(es) AgendaItem."""

    def afterSetUp(self):
        """ Initialization of user and AgendaItem
        """

        self.portal.portal_membership.addMember(
            'manager', 'secret', ['Manager'], [])
        self.login('manager')

        self.portal.evenementen.invokeFactory('MREvent', 'mymrevent')
        self.portal.evenementen.mymrevent.invokeFactory(
            'AgendaItem', 'myagendaitem')
        self.agendaitem = self.portal.evenementen.mymrevent.myagendaitem

    def test_IllegalCreation(self):
        """ Test if you are not allowed to create this content type
            if you are not inside an MREvent type.
        """

        self.assertRaises(ValueError,
                          self.portal.invokeFactory,
                          'AgendaItem',
                          'error')

    def test_Fields(self):
        """ Test if the AgendaItem has all the required fields
        """

        self.agendaitem.Title()             # Onderwerp
        self.agendaitem.getSpeaker()        # Spreker
        self.agendaitem.getOrganisation()   # Organisatie
        self.agendaitem.getSummary()        # Samenvatting
        self.agendaitem.getItemstartdate()  # Start tijd
        self.agendaitem.getItemenddate()    # Eind tijd

    def test_Existance(self):
        """ Test if the AgendaItem exists within portal_types
        """

        types_ = self.portal.portal_types.objectIds()
        self.failUnless('AgendaItem' in types_)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testAgendaItem))
    return suite
