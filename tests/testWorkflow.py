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
from AccessControl import Unauthorized
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
            ('reviewer', 'Member'),
            ('manager', 'Manager'),
        )
        membership = self.portal.portal_membership
        for memberId, role in MEMBERS:
            membership.addMember(memberId, 'secret', [role], [])

        self.workflow = self.portal.portal_workflow
        
        self.login('manager')
        self.contentContainer = self.portal.nieuwsbrieven.newsl_2006
        self.contentContainer.manage_addLocalRoles('author',['Author'])
        self.contentContainer.manage_addLocalRoles('reviewer',['Reviewer'])
        self.logout()

    # Manually created methods

    def test_private_state(self):
        """ Test if the private state has the correct rights
        """
        self.assertEqual(self._content_state(), 'private')
        self.assertCannotCreateContent('member','NewsLetter')
        self.assertCanCreateContent('author','NewsLetter')
        self.assertCannotCreateContent('cmember','NewsLetter')
        self.assertCannotCreateContent('reviewer','NewsLetter')
        self.assertCanCreateContent('manager','NewsLetter')
        self.assertHasTransitions('member')
        self.assertHasTransitions('author', ['restricted_publish'])
        self.assertHasTransitions('cmember')
        self.assertHasTransitions('reviewer', ['publish'])
        self.assertHasTransitions('manager',['restricted_publish','publish','submit'])

    def assertHasTransitions(self, memberId, possible=None):
        """Test the available transitions for a member.  The 'possible'
        param can be None, a string (for one transition) or a list of
        strings (multiple transitions).
        """
        
        if possible is None:
            possible = []
        elif isinstance(possible, basestring):
            possible = [possible]
        else:
            possible = list(possible)
            possible.sort()
        
        wfTool = getToolByName(self.portal, 'portal_workflow')
        container = self.contentContainer
       
        self.login('manager')
        container.invokeFactory('NewsLetter', 'someobj')
        self.logout()
         
        self.login(memberId) 
        transitions = wfTool.getTransitionsFor(container.someobj)
        transitions = [x['id'] for x in transitions]
        transitions.sort()
        self.assertEqual(possible, transitions)
        self.logout()

        self.login('manager')
        container.someobj.manage_delObjects(['someobj'])
        self.logout()

    def assertCannotCreateContent(self, memberId, type_, err=Unauthorized):
        container = self.contentContainer
        self.login(memberId)
        self.failUnlessRaises(err, container.invokeFactory, 
                              type_, 'someobj')
        self.logout()

    def assertCanCreateContent(self, memberId, type_):
        container = self.contentContainer
        self.login(memberId)
        container.invokeFactory(type_, 'someobj')
        self.failUnless('someobj' in container.contentIds())
        container.manage_delObjects(['someobj'])
        self.logout()

    def _content_state(self):
        """Return the current state of the NewsLetter content object.
        """

        wfTool = getToolByName(self.portal, 'portal_workflow')
        self.login('manager')
        self.contentContainer.invokeFactory('NewsLetter','newsletter')
        testletter = self.contentContainer.newsletter
        status = wfTool.getStatusOf('minaraad_workflow', testletter)
        self.logout()
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


