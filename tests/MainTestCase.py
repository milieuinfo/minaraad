# File: MainTestCase.py
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

#
# Base TestCase for minaraad
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

##code-section module-header #fill in your manual code here
##/code-section module-header

from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
from Products.minaraad.config import HAS_PLONE21
from Products.minaraad.config import PRODUCT_DEPENDENCIES
from Products.minaraad.config import DEPENDENCIES

# Add common dependencies
if not HAS_PLONE21:
    DEPENDENCIES.append('Archetypes')
    PRODUCT_DEPENDENCIES.append('MimetypesRegistry')
    PRODUCT_DEPENDENCIES.append('PortalTransforms')
PRODUCT_DEPENDENCIES.append('minaraad')

# Install all (product-) dependencies, install them too
for dependency in PRODUCT_DEPENDENCIES + DEPENDENCIES:
    ZopeTestCase.installProduct(dependency)

ZopeTestCase.installProduct('minaraad')

PRODUCTS = list()
PRODUCTS += DEPENDENCIES
PRODUCTS.append('minaraad')

testcase = PloneTestCase.PloneTestCase

##code-section module-before-plone-site-setup #fill in your manual code here
from zope.app.tests import placelesssetup
placelesssetup.setUp()
from Products.Five import zcml
from Products import minaraad, Five
##/code-section module-before-plone-site-setup

PloneTestCase.setupPloneSite(products=PRODUCTS)

class MainTestCase(testcase):
    """Base TestCase for minaraad."""

    ##code-section class-header_MainTestCase #fill in your manual code here
    ##/code-section class-header_MainTestCase

    # Commented out for now, it gets blasted at the moment anyway.
    # Place it in the protected section if you need it.
    #def afterSetup(self):
    #    """
    #    """
    #    pass
    
    def _setup(self):
        testcase._setup(self)
        
        # need to setup some Five stuff to get view lookups working
        zcml.load_config('meta.zcml', Five)
        zcml.load_config('permissions.zcml', Five)
        zcml.load_config('configure.zcml', minaraad)
        
        zcml.load_string('''<configure xmlns="http://namespaces.zope.org/zope"
           xmlns:five="http://namespaces.zope.org/five">
  <!-- basic collection of directives needed for proper traversal and request handling -->
  <include package="zope.app.traversing" />
  <adapter
      for="*"
      factory="Products.Five.traversable.FiveTraversable"
      provides="zope.app.traversing.interfaces.ITraversable"
      />
  <adapter
      for="*"
      factory="zope.app.traversing.adapters.Traverser"
      provides="zope.app.traversing.interfaces.ITraverser"
      />
  <five:implements class="ZPublisher.HTTPRequest.HTTPRequest"
                   interface="zope.publisher.interfaces.browser.IBrowserRequest"
                   />

</configure>''')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(MainTestCase))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


