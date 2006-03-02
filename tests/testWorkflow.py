# File: testWorkflow.py
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
# Test-cases for class(es) 
#

from Testing import ZopeTestCase
from Products.minaraad.config import *
from Products.minaraad.tests.MainTestCase import MainTestCase

# Import the tested classes

##code-section module-beforeclass #fill in your manual code here
from Products.CMFCore.utils import getToolByName
##/code-section module-beforeclass


class testWorkflow(MainTestCase):
    """Test-cases for class(es) ."""

    ##code-section class-header_testWorkflow #fill in your manual code here
    ##/code-section class-header_testWorkflow

    def afterSetUp(self):
        """ Make users for the tests and make a directory to work in
        """

        MEMBERS = (
            ('member', 'Member'),
            ('author', 'Member'),
            ('cmember', 'Council Member'),
            ('reviewer', 'Reviewer'),
            ('manager', 'Manager'),
        )
        membership = self.portal.portal_membership
        for memberId, role in MEMBERS:
            membership.addMember(memberId, 'secret', [role], [])

        self.workflow = self.portal.portal_workflow
        
        self.login('manager')
        self.portal.nieuwsbrieven.newsl_2006.invokeFactory('NewsLetter','newsletter')
        self.portal.nieuwsbrieven.newsl_2006.newsletter

    # Manually created methods

    def test_private_state(self):
        self.assertEqual(self._content_state(), 'private')

        wf = self.workflow

        self.login('manager')
        self.portal.invokeFactory('Folder', id='map')
        self.portal.map.manage_addLocalRoles('author',['Author'])
        # self.assertEqual(wf.getInfoFor(self.portal.map,'review_state'), 'private')
        # self.logout()

        # self.login('author')
        self.portal.map.invokeFactory('Document', id='document')
        doc = self.portal.map._getOb('document')

        self.failUnless(doc)
        # self.assertEqual(wf.getInfoFor(self.portal.map.document,'review_state'), 'private')
    def _content_state(self):
        """Return the current state of the NewsLetter content object.
        """

        wfTool = getToolByName(self.portal, 'portal_workflow')
        testletter = self.portal.nieuwsbrieven.newsl_2006.newsletter
        status = wfTool.getStatusOf('minaraad_workflow', testletter)
        return status['review_state']


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testWorkflow))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


