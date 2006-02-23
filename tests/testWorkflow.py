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
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.PloneTestCase.setup import default_user
##/code-section module-beforeclass


class testWorkflow(MainTestCase):
    """Test-cases for class(es) ."""

    ##code-section class-header_testWorkflow #fill in your manual code here
    ##/code-section class-header_testWorkflow

    def afterSetUp(self):
        """ Make users for the tests and make a directory to work in
        """
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.userfolder = self.portal.acl_users
        self.default_user = default_user

        self.userfolder._doAddUser('member', 'secret', ['Member'], [])
        self.userfolder._doAddUser('author', 'secret', ['Member'], [])
        self.userfolder._doAddUser('reviewer', 'secret', ['Reviewer'], [])
        self.userfolder._doAddUser('manager', 'secret', ['Manager'], [])
        self.userfolder._doAddUser('cmember', 'secret', ['Council Member'], [])


    # Manually created methods

    def test_private_state(self):
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

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testWorkflow))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


