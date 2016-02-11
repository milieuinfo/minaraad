# -*- coding: utf-8 -*-
#
# File: testSetup.py
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


import sets

from Products.minaraad.tests.MainTestCase import MainTestCase
from Products.minaraad.tests.utils import load_file
ATTACHMENT = load_file('test.pdf')


class testSetup(MainTestCase):
    """ Test cases for the generic setup of the product
    """

    def test_types(self):
        """
        """
        ids = self.portal.portal_types.objectIds()
        self.failUnless('Document' in ids)
        self.failUnless('Advisory' in ids)
        self.failUnless('FileAttachment' in ids)

    def test_skins(self):
        """
        """
        ids = self.portal.portal_skins.objectIds()
        self.failUnless('minaraad' in ids)

    def test_workflows(self):
        """
        """
        ids = self.portal.portal_workflow.objectIds()
        self.failUnless('minaraad_workflow' in ids)

    def test_workflowChains(self):
        """
        """
        getChain = self.portal.portal_workflow.getChainForPortalType
        self.failUnless('minaraad_workflow' in getChain('Hearing'))

    def test_reinstall(self):
        qi = self.portal.portal_quickinstaller
        qi.reinstallProducts(('minaraad', ))

    def test_cookieTimeOutProperty(self):
        propsTool = self.portal.portal_properties
        siteProperties = propsTool.site_properties
        cookieLength = siteProperties.getProperty('auth_cookie_length', 0)
        self.failUnless(cookieLength == 30)

    def test_memberDataToolProperties(self):

        # new properties we add
        newFields = sets.Set(('company', 'jobtitle', 'street', 'housenumber',
                              'zipcode', 'city', 'phonenumber', 'genders',
                              'gender', 'country', 'select_country',
                              'firstname', 'bus'))

        tool = self.portal.portal_memberdata

        properties = sets.Set(tool.propertyIds())

        self.failUnless(newFields.issubset(properties),
                        "%r missing from portal_memberdata." %
                        list(newFields - properties))

        # make sure if we add an additional value, its not found in the real
        # properties
        newFields.add(1)
        self.failIf(newFields.issubset(properties))

    def test_memberAreaCreation(self):
        userfolder = self.portal.acl_users
        userfolder._doAddUser('member', 'secret', ['Member'], [])
        self.login('member')
        if hasattr(self.portal, 'Members'):
            self.failIf('member' in self.portal.Members.objectIds())

        membership = self.portal.portal_membership
        self.failIf(membership.getMemberareaCreationFlag())

    def test_minaraadProperties(self):
        propsTool = self.portal.portal_properties

        self.failUnless(hasattr(propsTool, 'minaraad_properties'))

        props = propsTool.minaraad_properties
        self.failUnless(props.hasProperty('themes'))

    def test_pdf_indexing_file(self):
        self.loginAsPortalOwner()
        catalog = self.portal.portal_catalog
        results = catalog(SearchableText='Zest')
        self.assertEquals(len(results), 0)

        self.portal.invokeFactory('File', 'file')
        f = self.portal.file
        f.setFile(ATTACHMENT)
        f.reindexObject()

        results = catalog(SearchableText='Zest')
        self.assertEquals(len(results), 1)
        self.assertEquals(results[0].getObject(), f)

    def test_catalog_finds_attachment_content(self):
        self.loginAsPortalOwner()
        catalog = self.portal.portal_catalog
        results = catalog(SearchableText='Zest')
        self.assertEquals(len(results), 0)

        self.portal.adviezen.adv_2006.invokeFactory('Advisory', 'advisory')
        advisory = self.portal.adviezen.adv_2006.advisory
        # Note that invokeFactory is not working when you use the
        # roadrunner tests as the FileAttachment type from
        # SimpleAttachment is not available for some reason.
        advisory.invokeFactory(type_name='FileAttachment', id='attachment',
                               file=ATTACHMENT)
        advisory.reindexObject()
        advisory.attachment.reindexObject()

        results = catalog(portal_type='Advisory', SearchableText='Zest')
        self.assertEquals(len(results), 1)
        self.assertEquals(results[0].getObject(), advisory)

        # Note that this search should also give just 1 result without
        # the portal_type restriction as searching for FileAttachments
        # is not allowed, but it seems this restriction is only done
        # in the UI.  We will check that like this:
        site_props = self.portal.portal_properties.site_properties
        self.failUnless('FileAttachment' in site_props.types_not_searched)

    def test_controlPanel(self):
        from Products.CMFCore.utils import getToolByName
        controlPanel = getToolByName(self.portal, 'portal_controlpanel')
        actions = controlPanel.listActions()

        invisible_controlpanel_actions = ('ZMI', )
        for action in actions:
            if action.id in invisible_controlpanel_actions:
                self.assertEqual(action.visible, 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testSetup))
    return suite
