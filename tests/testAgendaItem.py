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

__author__ = """Rocky Burt <r.burt@zestsoftware.nl>"""
__docformat__ = 'plaintext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

##code-section module-header #fill in your manual code here
##/code-section module-header

#
# Test-cases for class(es) AgendaItem
#

from Testing import ZopeTestCase
from Products.minaraad.config import *
from Products.minaraad.tests.MainTestCase import MainTestCase

# Import the tested classes
from Products.minaraad.content.AgendaItem import AgendaItem

##code-section module-beforeclass #fill in your manual code here
##/code-section module-beforeclass


class testAgendaItem(MainTestCase):
    """Test-cases for class(es) AgendaItem."""

    ##code-section class-header_testAgendaItem #fill in your manual code here
    ##/code-section class-header_testAgendaItem

    def afterSetUp(self):
        """ Initialization of user and AgendaItem
        """
        
        self.portal.portal_membership.addMember('manager','secret',['Manager'],[])
        self.login('manager')

	self.portal.hoorzittingen.invokeFactory('Hearing','myhoorzitting')
        self.portal.hoorzittingen.myhoorzitting.invokeFactory('AgendaItem','myagendaitem')
        self.agendaitem = self.portal.hoorzittingen.myhoorzitting.myagendaitem

    # Manually created methods

    def test_IllegalCreation(self):
        """ Test if you are not allowed to create this content type
            if you are not inside a Hearing type
        """

        self.assertRaises(ValueError,
                          self.portal.invokeFactory,
                          'AgendaItem',
                          'error')

    def test_Fields(self):
        """ Test if the AgendaItem has all the required fields
        """

        self.agendaitem.Title()            # Onderwerp
        self.agendaitem.getSpeaker()       # Spreker
        self.agendaitem.getOrganisation()  # Organisatie
        self.agendaitem.getSummary()       # Samenvatting
        self.agendaitem.getItemstartdate() # Start tijd
        self.agendaitem.getItemenddate()   # Eind tijd
        self.agendaitem.getAttachments()   # Bijlage(n)

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

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


