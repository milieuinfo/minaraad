# -*- coding: utf-8 -*-
#
# File: utils.py
#
# Copyright (c) 2006 by Zest Software
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

import os
import Products.minaraad.tests
from zope.app.testing import setup
from Products.Five import zcml
from Products import minaraad, Five
from Products import TextIndexNG3

def load_file(name, size=0):
    """Load file from testing directory
    """

    test_dir = os.path.dirname(Products.minaraad.tests.__file__)

    full_path = os.path.join(test_dir, name)
    
    fd = open(full_path, 'rb')
    data = fd.read()
    fd.close()
    return data

def setup_CA():
    setup.placefulSetUp()
    # need to setup some Five stuff to get view lookups working
    zcml.load_config('meta.zcml', Five)
    zcml.load_config('permissions.zcml', Five)
    zcml.load_config('configure.zcml', Five.site)

    zcml.load_config('configure.zcml', TextIndexNG3)
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
