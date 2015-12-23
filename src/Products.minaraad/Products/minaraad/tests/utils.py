# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import WorkflowException
import Products.minaraad.tests
import os


def load_file(name, size=0):
    """Load file from testing directory
    """

    test_dir = os.path.dirname(Products.minaraad.tests.__file__)

    full_path = os.path.join(test_dir, name)

    fd = open(full_path, 'rb')
    data = fd.read()
    fd.close()
    return data


def _createNode(portal, item):
    workflow_tool = getToolByName(portal, 'portal_workflow')
    id = item['id']
    type = item['type']

    if id not in portal.objectIds():
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
