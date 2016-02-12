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


from Products.minaraad.tests.MainTestCase import MainTestCase

from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions


class testWorkflow(MainTestCase):
    """Test-cases for class(es) ."""

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
            self.assureRoles([role])
            membership.addMember(memberId, 'secret', [role], [])

        self.workflow = self.portal.portal_workflow

        self.login('manager')
        self.contentContainer = self.portal.nieuwsbrieven.newsl_2006
        self.contentContainer.manage_addLocalRoles('author', ['Author'])
        self.contentContainer.manage_addLocalRoles('reviewer', ['Reviewer'])
        self.contentContainer.invokeFactory('NewsLetter', 'someobj')

        self.contentContainer.invokeFactory('NewsLetter', 'private')
        self.contentContainer.invokeFactory('NewsLetter', 'restricted')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer.restricted,
                           'restricted_publish')
        self.contentContainer.invokeFactory('NewsLetter', 'pending_private')
        wfTool.doActionFor(self.contentContainer.pending_private, 'submit')
        self.contentContainer.invokeFactory('NewsLetter', 'published_nl')
        wfTool.doActionFor(self.contentContainer.published_nl, 'publish')
        self.contentContainer.invokeFactory('NewsLetter', 'revisioning')
        wfTool.doActionFor(self.contentContainer.revisioning, 'publish')
        wfTool.doActionFor(self.contentContainer.revisioning, 'revise')
        self.contentContainer.invokeFactory('NewsLetter',
                                            'pending_revisioning')
        wfTool.doActionFor(self.contentContainer.pending_revisioning,
                           'publish')
        wfTool.doActionFor(self.contentContainer.pending_revisioning,
                           'revise')
        wfTool.doActionFor(self.contentContainer.pending_revisioning,
                           'submit2')

        self.logout()

    def test_pending_private_state(self):
        """ Test if the pending_private state has the correct rights
        """
        self.login('manager')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer.someobj, 'submit')
        self.logout()

        self.assertEqual(self._content_state(), 'pending_private')
        self.assertHasTransitions('member')
        self.assertHasTransitions('author', ['retract'])
        self.assertHasTransitions('cmember')
        self.assertHasTransitions('reviewer', ['publish', 'reject'])
        self.assertHasTransitions('manager', ['publish', 'reject', 'retract'])

        self.login('manager')
        wfTool.doActionFor(self.contentContainer.someobj, 'retract')
        self.logout()

    def _folder_state(self):
        """Return the current state of the nieuwsbrieven folder object.
        """

        wfTool = getToolByName(self.portal, 'portal_workflow')
        self.login('manager')
        testfolder = self.contentContainer
        status = wfTool.getInfoFor(testfolder, 'review_state', '')
        self.logout()
        return status

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
            possible = sorted(possible)

        wfTool = getToolByName(self.portal, 'portal_workflow')
        container = self.contentContainer

        self.login(memberId)
        transitions = wfTool.getTransitionsFor(container.someobj)
        transitions = sorted([x['id'] for x in transitions])
        self.assertEqual(possible, transitions)
        self.logout()

    def test_private_state(self):
        """ Test if the private state has the correct rights
        """
        self.assertEqual(self._content_state(), 'private')
        self.assertCannotCreateContent('member', 'NewsLetter')
        self.assertCanCreateContent('author', 'NewsLetter')
        self.assertCannotCreateContent('cmember', 'NewsLetter')
        self.assertCannotCreateContent('reviewer', 'NewsLetter')
        self.assertCanCreateContent('manager', 'NewsLetter')
        self.assertHasTransitions('member')
        self.assertHasTransitions('author', ['restricted_publish', 'submit'])
        self.assertHasTransitions('cmember')
        self.assertHasTransitions('reviewer',
                                  ['restricted_publish', 'publish'])
        self.assertHasTransitions('manager',
                                  ['restricted_publish', 'publish', 'submit'])

    def test_cmember_permissions(self):
        """ Test if the council member has the correct permissions on CTs
        """
        self.login('cmember')
        checkPermission = self.portal.portal_membership.checkPermission

        obj = self.contentContainer.private
        self.failIf(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.restricted
        self.failUnless(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.pending_private
        self.failIf(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.published_nl
        self.failUnless(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.revisioning
        self.failUnless(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.pending_revisioning
        self.failUnless(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        self.logout()

    def test_author_permissions(self):
        """ Test if the author has the correct permissions on CTs
        """
        self.login('author')
        checkPermission = self.portal.portal_membership.checkPermission

        obj = self.contentContainer.private
        self.failUnless(checkPermission(permissions.View, obj))
        self.failUnless(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.restricted
        self.failUnless(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.pending_private
        self.failUnless(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.published_nl
        self.failUnless(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.revisioning
        self.failUnless(checkPermission(permissions.View, obj))
        self.failUnless(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.pending_revisioning
        self.failUnless(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        self.logout()

    def test_folder_pending_state(self):
        """ Test if the folder restricted state has the correct rights
        """
        self.assertEqual(self._folder_state(), 'published')
        self.login('manager')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer, 'retract')
        wfTool.doActionFor(self.contentContainer, 'submit')
        self.logout()

        self.assertEqual(self._folder_state(), 'pending')
        self.assertFolderTransitions('member')
        self.assertFolderTransitions('author', ['retract2'])
        self.assertFolderTransitions('cmember')
        self.assertFolderTransitions('reviewer', ['publish', 'reject'])
        self.assertFolderTransitions('manager',
                                     ['publish', 'reject', 'retract2'])

        self.login('manager')
        wfTool.doActionFor(self.contentContainer, 'retract2')
        self.logout()

    def test_folder_private_state(self):
        """ Test if the folder private state has the correct rights
        """
        self.login('manager')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer, 'retract')
        self.logout()
        self.assertEqual(self._folder_state(), 'private')
        self.assertFolderTransitions('member')
        self.assertFolderTransitions('author', 'submit')
        self.assertFolderTransitions('cmember')
        self.assertFolderTransitions('reviewer',
                                     ['publish', 'restricted_publish'])
        self.assertFolderTransitions(
            'manager', ['publish', 'restricted_publish', 'submit'])

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
            possible = sorted(possible)

        wfTool = getToolByName(self.portal, 'portal_workflow')
        container = self.contentContainer

        self.login(memberId)
        transitions = wfTool.getTransitionsFor(container)
        transitions = sorted([x['id'] for x in transitions])
        self.assertEqual(possible, transitions)
        self.logout()

    def test_manager_permissions(self):
        """ Test if the manager has the correct permissions on CTs
        """
        self.login('manager')
        checkPermission = self.portal.portal_membership.checkPermission

        obj = self.contentContainer.private
        self.failUnless(checkPermission(permissions.View, obj))
        self.failUnless(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.restricted
        self.failUnless(checkPermission(permissions.View, obj))
        self.failUnless(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.pending_private
        self.failUnless(checkPermission(permissions.View, obj))
        self.failUnless(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.published_nl
        self.failUnless(checkPermission(permissions.View, obj))
        self.failUnless(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.revisioning
        self.failUnless(checkPermission(permissions.View, obj))
        self.failUnless(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.pending_revisioning
        self.failUnless(checkPermission(permissions.View, obj))
        self.failUnless(checkPermission(permissions.ModifyPortalContent, obj))

        self.logout()

    def test_restricted_state(self):
        """ Test if the restricted state has the correct rights
        """
        self.login('manager')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer.someobj, 'restricted_publish')
        self.logout()

        self.assertEqual(self._content_state(), 'restricted')
        self.assertHasTransitions('member')
        self.assertHasTransitions('author', ['retract'])
        self.assertHasTransitions('cmember')
        self.assertHasTransitions('reviewer', 'publish')
        self.assertHasTransitions('manager', ['retract', 'publish'])

        self.login('manager')
        wfTool.doActionFor(self.contentContainer.someobj, 'retract')
        self.logout()

    def assertCannotCreateContent(self, memberId, type_):
        container = self.contentContainer
        self.login(memberId)
        try:
            container.invokeFactory(type_, 'someotherobj')
            created = True
        except ValueError:
            created = False
        except Unauthorized:
            created = False

        assert not created
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

    def test_folder_published_state(self):
        """ Test if the folder published state has the correct rights
        """
        self.assertEqual(self._folder_state(), 'published')
        self.assertFolderTransitions('member')
        self.assertFolderTransitions('author')
        self.assertFolderTransitions('cmember')
        self.assertFolderTransitions('reviewer',
                                     ['retract', 'restricted_publish'])
        self.assertFolderTransitions('manager',
                                     ['retract', 'restricted_publish'])

        self.login('manager')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer, 'retract')
        self.logout()

    def test_published_state(self):
        """ Test if the published state has the correct rights
        """
        self.login('manager')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer.someobj, 'publish')
        self.logout()

        self.assertEqual(self._content_state(), 'published')
        self.assertHasTransitions('member')
        self.assertHasTransitions('author', ['revise', 'restricted_publish'])
        self.assertHasTransitions('cmember')
        self.assertHasTransitions('reviewer',
                                  ['reject', 'revise', 'restricted_publish'])
        self.assertHasTransitions('manager',
                                  ['reject', 'revise', 'restricted_publish'])

        self.login('manager')
        wfTool.doActionFor(self.contentContainer.someobj, 'reject')
        self.logout()

    def test_reviewer_permissions(self):
        """ Test if the reviewer has the correct permissions on CTs
        """
        self.login('reviewer')
        checkPermission = self.portal.portal_membership.checkPermission

        obj = self.contentContainer.private
        self.failUnless(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.restricted
        self.failUnless(checkPermission(permissions.View, obj))
        self.failUnless(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.pending_private
        self.failUnless(checkPermission(permissions.View, obj))
        self.failUnless(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.published_nl
        self.failUnless(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.revisioning
        self.failUnless(checkPermission(permissions.View, obj))
        self.failUnless(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.pending_revisioning
        self.failUnless(checkPermission(permissions.View, obj))
        self.failUnless(checkPermission(permissions.ModifyPortalContent, obj))

        self.logout()

    def test_folder_restricted_state(self):
        """ Test if the folder restricted state has the correct rights
        """
        self.login('manager')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer, 'restricted_publish')
        self.logout()

        self.assertEqual(self._folder_state(), 'restricted')
        self.assertFolderTransitions('member')
        self.assertFolderTransitions('author')
        self.assertFolderTransitions('cmember')
        self.assertFolderTransitions('reviewer', ['publish', 'retract'])
        self.assertFolderTransitions('manager', ['publish', 'retract'])

        self.login('manager')
        wfTool.doActionFor(self.contentContainer, 'retract')
        self.logout()

    def test_revisioning_state(self):
        """ Test if the revisioning state has the correct rights
        """
        self.login('manager')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer.someobj, 'publish')
        wfTool.doActionFor(self.contentContainer.someobj, 'revise')
        self.logout()

        self.assertEqual(self._content_state(), 'revisioning')
        self.assertHasTransitions('member')
        self.assertHasTransitions('author', ['submit2'])
        self.assertHasTransitions('cmember')
        self.assertHasTransitions('reviewer', ['publish'])
        self.assertHasTransitions('manager', ['publish', 'submit2'])

        self.login('manager')
        wfTool.doActionFor(self.contentContainer.someobj, 'publish')
        wfTool.doActionFor(self.contentContainer.someobj, 'reject')
        self.logout()

    def test_member_permissions(self):
        """ Test if the member has the correct permissions on CTs
        """
        self.login('member')
        checkPermission = self.portal.portal_membership.checkPermission

        obj = self.contentContainer.private
        self.failIf(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.restricted
        self.failIf(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.pending_private
        self.failIf(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.published_nl
        self.failUnless(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.revisioning
        self.failUnless(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        obj = self.contentContainer.pending_revisioning
        self.failUnless(checkPermission(permissions.View, obj))
        self.failIf(checkPermission(permissions.ModifyPortalContent, obj))

        self.logout()

    def test_pending_revisioning_state(self):
        """ Test if the pending_revisioning state has the correct rights
        """
        self.login('manager')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(self.contentContainer.someobj, 'publish')
        wfTool.doActionFor(self.contentContainer.someobj, 'revise')
        wfTool.doActionFor(self.contentContainer.someobj, 'submit2')
        self.logout()

        self.assertEqual(self._content_state(), 'pending_revisioning')
        self.assertHasTransitions('member')
        self.assertHasTransitions('author', ['retract2'])
        self.assertHasTransitions('cmember')
        self.assertHasTransitions('reviewer', ['publish', 'reject2'])
        self.assertHasTransitions('manager',
                                  ['publish', 'reject2', 'retract2'])

        self.login('manager')
        wfTool.doActionFor(self.contentContainer.someobj, 'publish')
        wfTool.doActionFor(self.contentContainer.someobj, 'reject')
        self.logout()

    def assertCanCreateContent(self, memberId, type_):
        container = self.contentContainer
        self.login(memberId)
        container.invokeFactory(type_, 'someotherobj')
        self.failUnless('someotherobj' in container.contentIds())
        container.manage_delObjects(['someotherobj'])
        self.logout()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testWorkflow))
    return suite
