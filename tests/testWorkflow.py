# -*- coding: utf-8 -*-
#
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
        self.contentContainer.invokeFactory('NewsLetter', 'someobj')
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
        self.assertHasTransitions('author', ['restricted_publish','submit'])
        self.assertHasTransitions('cmember')
        self.assertHasTransitions('reviewer', ['restricted_publish','publish'])
        self.assertHasTransitions('manager',['restricted_publish','publish','submit'])

    def test_folder_pending_state(self):
        """ Test if the folder restricted state has the correct rights
        """
        self.login('manager')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer,'submit')
        self.logout()

        self.assertEqual(self._folder_state(),'pending')
        self.assertFolderTransitions('member')
        self.assertFolderTransitions('author',['retract2'])
        self.assertFolderTransitions('cmember')
        self.assertFolderTransitions('reviewer',['publish','reject'])
        self.assertFolderTransitions('manager',['publish','reject','retract2'])

        self.login('manager')
        wfTool.doActionFor(self.contentContainer,'retract2')
        self.logout()

    def test_pending_private_state(self):
        """ Test if the pending_private state has the correct rights
        """
        self.login('manager')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer.someobj,'submit')
        self.logout()

        self.assertEqual(self._content_state(),'pending_private') 
        self.assertHasTransitions('member')
        self.assertHasTransitions('author', ['retract'])
        self.assertHasTransitions('cmember')
        self.assertHasTransitions('reviewer', ['publish','reject'])
        self.assertHasTransitions('manager',['publish','reject','retract'])

        self.login('manager')
        wfTool.doActionFor(self.contentContainer.someobj,'retract')
        self.logout() 

    def _folder_state(self):
        """Return the current state of the nieuwsbrieven folder object.
        """

        wfTool = getToolByName(self.portal, 'portal_workflow')
        self.login('manager')
        testfolder = self.contentContainer
        status = wfTool.getInfoFor(testfolder,'review_state','')
        self.logout()
        return status

    def test_published_state(self):
        """ Test if the published state has the correct rights
        """
        self.login('manager')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer.someobj,'publish')
        self.logout()

        self.assertEqual(self._content_state(),'published') 
        self.assertHasTransitions('member')
        self.assertHasTransitions('author', ['revise'])
        self.assertHasTransitions('cmember')
        self.assertHasTransitions('reviewer', ['reject','revise'])
        self.assertHasTransitions('manager',['reject','revise'])

        self.login('manager')
        wfTool.doActionFor(self.contentContainer.someobj,'reject')
        self.logout()
 
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
       
        self.login(memberId) 
        transitions = wfTool.getTransitionsFor(container.someobj)
        transitions = [x['id'] for x in transitions]
        transitions.sort()
        self.assertEqual(possible, transitions)
        self.logout()

    def test_restricted_state(self):
        """ Test if the restricted state has the correct rights
        """
        self.login('manager')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer.someobj,'restricted_publish')
        self.logout()

        self.assertEqual(self._content_state(),'restricted') 
        self.assertHasTransitions('member')
        self.assertHasTransitions('author', ['retract'])
        self.assertHasTransitions('cmember')
        self.assertHasTransitions('reviewer')
        self.assertHasTransitions('manager',['retract'])

        self.login('manager')
        wfTool.doActionFor(self.contentContainer.someobj,'retract')
        self.logout()
   
    def test_revisioning_state(self):
        """ Test if the revisioning state has the correct rights
        """
        self.login('manager')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer.someobj,'publish')
        wfTool.doActionFor(self.contentContainer.someobj,'revise')
        self.logout()

        self.assertEqual(self._content_state(),'revisioning') 
        self.assertHasTransitions('member')
        self.assertHasTransitions('author')
        self.assertHasTransitions('cmember')
        self.assertHasTransitions('reviewer', ['publish'])
        self.assertHasTransitions('manager',['publish','submit2'])

        self.login('manager')
        wfTool.doActionFor(self.contentContainer.someobj,'publish')
        wfTool.doActionFor(self.contentContainer.someobj,'reject')
        self.logout()

    def assertCannotCreateContent(self, memberId, type_, err=Unauthorized):
        container = self.contentContainer
        self.login(memberId)
        self.failUnlessRaises(err, container.invokeFactory, 
                              type_, 'someotherobj')
        self.logout()

    def test_pending_revisioning_state(self):
        """ Test if the pending_revisioning state has the correct rights
        """
        self.login('manager')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer.someobj,'publish')
        wfTool.doActionFor(self.contentContainer.someobj,'revise')
        wfTool.doActionFor(self.contentContainer.someobj,'submit2')
        self.logout()

        self.assertEqual(self._content_state(),'pending_revisioning') 
        self.assertHasTransitions('member')
        self.assertHasTransitions('author')
        self.assertHasTransitions('cmember')
        self.assertHasTransitions('reviewer', ['publish','reject2'])
        self.assertHasTransitions('manager',['publish','reject2','retract2'])

        self.login('manager')
        wfTool.doActionFor(self.contentContainer.someobj,'publish')
        wfTool.doActionFor(self.contentContainer.someobj,'reject')
        self.logout()

    def assertCanCreateContent(self, memberId, type_):
        container = self.contentContainer
        self.login(memberId)
        container.invokeFactory(type_, 'someotherobj')
        self.failUnless('someotherobj' in container.contentIds())
        container.manage_delObjects(['someotherobj'])
        self.logout()

    def test_folder_private_state(self):
        """ Test if the folder private state has the correct rights
        """
        self.assertEqual(self._folder_state(),'private')
        self.assertFolderTransitions('member')
        self.assertFolderTransitions('author','submit')
        self.assertFolderTransitions('cmember')
        self.assertFolderTransitions('reviewer',['publish','publish_internal'])
        self.assertFolderTransitions('manager',['publish','publish_internal','submit'])
        
    def test_folder_restricted_state(self):
        """ Test if the folder restricted state has the correct rights
        """
        self.login('manager')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer,'publish_internal')
        self.logout()

        self.assertEqual(self._folder_state(),'restricted')
        self.assertFolderTransitions('member')
        self.assertFolderTransitions('author')
        self.assertFolderTransitions('cmember')
        self.assertFolderTransitions('reviewer',['retract'])
        self.assertFolderTransitions('manager',['retract'])

        self.login('manager')
        wfTool.doActionFor(self.contentContainer,'retract')
        self.logout()

    def test_folder_published_state(self):
        """ Test if the folder published state has the correct rights
        """
        self.login('manager')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer,'publish')
        self.logout()

        self.assertEqual(self._folder_state(),'published')
        self.assertFolderTransitions('member')
        self.assertFolderTransitions('author')
        self.assertFolderTransitions('cmember')
        self.assertFolderTransitions('reviewer',['retract'])
        self.assertFolderTransitions('manager',['retract'])

        self.login('manager')
        wfTool.doActionFor(self.contentContainer,'retract')
        self.logout()

    def assertFolderTransitions(self, memberId, possible=None):
        """Test the available transitions for a member. The 'possible'
           param can be None, a string (for one transition) or a list
           of strings (multiple transitions).
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
       
        self.login(memberId) 
        transitions = wfTool.getTransitionsFor(container)
        transitions = [x['id'] for x in transitions]
        transitions.sort()
        self.assertEqual(possible, transitions)
        self.logout()

    def _content_state(self):
        """Return the current state of the NewsLetter content object.
        """

        wfTool = getToolByName(self.portal, 'portal_workflow')
        self.login('manager')
        testletter = self.contentContainer.someobj
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


