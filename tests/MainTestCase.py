# File: MainTestCase.py
"""\
unknown

"""
# Copyright (c) 2005 by Zest software 2005
# Generator: ArchGenXML Version 1.4 devel 4 http://sf.net/projects/archetypes/
#
# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#
__author__  = '''Rocky Burt <r.burt@zestsoftware.nl>'''
__docformat__ = 'plaintext'

##code-section module-header #fill in your manual code here
##/code-section module-header

#
# Base TestCase for xxx_name_this
#
from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase

ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('PortalTransforms', quiet=1)
ZopeTestCase.installProduct('MimetypesRegistry', quiet=1)
ZopeTestCase.installProduct('xxx_name_this')
# If the products's config includes DEPENDENCIES, install them too
try:
    from Products.xxx_name_this.config import DEPENDENCIES
except:
    DEPENDENCIES = []
for dependency in DEPENDENCIES:
    ZopeTestCase.installProduct(dependency)

PRODUCTS = ('Archetypes', 'xxx_name_this')

testcase = PloneTestCase.PloneTestCase
PloneTestCase.setupPloneSite(products=PRODUCTS)

class MainTestCase(testcase):
    """ Base TestCase for xxx_name_this"""
    ##code-section class-header_MainTestCase #fill in your manual code here
    ##/code-section class-header_MainTestCase

    # Commented out for now, it gets blasted at the moment anyway.
    # Place it in the protected section if you need it.
    #def afterSetUp(self):
    #    """
    #    """
    #    pass

##code-section module-footer #fill in your manual code here
##/code-section module-footer



