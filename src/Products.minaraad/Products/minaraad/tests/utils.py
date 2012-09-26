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
from Zope2.App import zcml

from Products import minaraad, Five, GenericSetup
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import WorkflowException


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
    zcml.load_config('meta.zcml', GenericSetup)

    zcml.load_config('configure.zcml', minaraad)

    zcml.load_string('''<configure xmlns="http://namespaces.zope.org/zope"
           xmlns:five="http://namespaces.zope.org/five">
  <!-- basic collection of directives needed for proper traversal and request
       handling -->
  <include package="zope.traversing" />
  <adapter
      for="*"
      factory="Products.Five.traversable.FiveTraversable"
      provides="zope.traversing.interfaces.ITraversable"
      />
  <adapter
      for="*"
      factory="zope.traversing.adapters.Traverser"
      provides="zope.traversing.interfaces.ITraverser"
      />
  <five:implements
      class="ZPublisher.HTTPRequest.HTTPRequest"
      interface="zope.publisher.interfaces.browser.IBrowserRequest"
      />

</configure>''')


def _createNode(portal, item):
    workflow_tool = getToolByName(portal, 'portal_workflow')
    id = item['id']
    type = item['type']

    if not id in portal.objectIds():
        portal.invokeFactory(type, id=id)
    created_object = portal._getOb(id, None)
    created_object.setTitle(item['title'])

    try:
        workflow_tool.doActionFor(created_object, 'publish')
    except WorkflowException:
        pass

    for child in item['children']:
        _createNode(created_object, child)


def print_error_log_on_wrong_browser_status(browser, portal):
    # First, if things go really wrong, then we cannot even get the
    # headers, and you can get errors like:
    # AttributeError: 'NoneType' object has no attribute 'tell'
    # BrowserStateError: not viewing any document
    try:
        browser.headers
    except AttributeError:
        print "No headers in browser, so something is really wrong."
    else:
        if str(browser.headers['status']).startswith('200'):
            return
        print "Browser status: ", browser.headers['status']
    if portal.error_log.getLogEntries():
        print "error_log entries: ", len(portal.error_log.getLogEntries())
        entry = portal.error_log.getLogEntries()[-1]
        # print last three lines of the traceback
        print '\n'.join(entry['tb_text'].splitlines()[-3:])
