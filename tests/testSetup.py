# File: testSetup.py
#
# Copyright (c) 2006 by Zest Software
# Generator: ArchGenXML Version 1.4.1 svn/devel
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
import sets
##/code-section module-header

#
# Setup tests
#

import os, sys
from Testing import ZopeTestCase
from Products.minaraad.tests.MainTestCase import MainTestCase

class testSetup(MainTestCase):
    """ Test cases for the generic setup of the product
    """

    ##code-section class-header_testSetup #fill in your manual code here
    ##/code-section class-header_testSetup

    def afterSetUp(self):
        """ 
        """
        pass

    def test_tools(self):
        """ 
        """
        ids = self.portal.objectIds()
        self.failUnless('archetype_tool' in ids)
        #[]

    def test_types(self):
        """ 
        """
        ids = self.portal.portal_types.objectIds()
        self.failUnless('Document' in ids)
        # ...

    def test_skins(self):
        """ 
        """
        ids = self.portal.portal_skins.objectIds()
        self.failUnless('plone_templates' in ids)
        # ...

    def test_workflows(self):
        """ 
        """
        ids = self.portal.portal_workflow.objectIds()
        self.failUnless('plone_workflow' in ids)
        # ...

    def test_workflowChains(self):
        """ 
        """
        getChain = self.portal.portal_workflow.getChainForPortalType
        self.failUnless('minaraad_workflow' in getChain('Document'))
        # ...

    # Manually created methods
    def test_memberDataToolProperties(self):
        # original memberdata properties
        baseFields = sets.Set(('visible_ids', 'last_login_time', 'language', 
                               'home_page', 'description', 'wysiwyg_editor', 
                               'error_log_update', 'location', 'portal_skin', 
                               'fullname', 'login_time', 'email', 'ext_editor', 
                               'listed'))
        
        # new properties we add
        newFields = sets.Set(('company', 'jobtitle', 'street', 'housenumber', 
                              'zipcode', 'city', 'phonenumber', 'genders', 
                              'gender', 'country', 'select_country', 
                              'other_country'))
    
        tool = self.portal.portal_memberdata

        # build up a complete set of what properties should now be in the tool
        fullFields = sets.Set(tuple(baseFields)+tuple(newFields))
        properties = sets.Set(tool.propertyIds())
        
        self.failUnless(fullFields == properties)
        
        # make sure if we add an additional value, its not found in the real
        # properties
        fullFields.add(1)
        self.failIf(fullFields == properties)

        
        
        


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testSetup))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


