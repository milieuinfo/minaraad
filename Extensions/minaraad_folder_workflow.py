# -*- coding: utf-8 -*-
#
# File: minaraad.py
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


from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.minaraad.config import *

productname = 'minaraad'


def setupminaraad_folder_workflow(self, workflow):
    """Define the minaraad_folder_workflow workflow.
    """
    # Add additional roles to portal
    portal = getToolByName(self,'portal_url').getPortalObject()
    data = list(portal.__ac_roles__)
    for role in ['Author', 'Council Member']:
        if not role in data:
            data.append(role)
    portal.__ac_roles__ = tuple(data)

    workflow.setProperties(title='minaraad_folder_workflow')

    for s in ['restricted', 'published', 'pending', 'private']:
        workflow.states.addState(s)

    for t in ['restricted_publish', 'publish', 'retract2', 'retract', 'reject', 'submit']:
        workflow.transitions.addTransition(t)

    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        workflow.variables.addVariable(v)

    workflow.addManagedPermission('Access contents information')
    workflow.addManagedPermission('View')
    workflow.addManagedPermission('Modify portal content')
    workflow.addManagedPermission('List folder contents')

    for l in ['my_workflow']:
        if not l in workflow.worklists.objectValues():
            workflow.worklists.addWorklist(l)

    ## Initial State

    workflow.states.setInitialState('private')

    ## States initialization

    stateDef = workflow.states['restricted']
    stateDef.setProperties(title="""restricted""",
                           transitions=['retract', 'publish'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Owner', 'Author', 'Council Member', 'Reviewer', 'Manager'])
    stateDef.setPermission('View',
                           0,
                           ['Owner', 'Author', 'Council Member', 'Reviewer', 'Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Reviewer', 'Manager'])
    stateDef.setPermission('List folder contents',
                           0,
                           ['Owner', 'Author', 'Council Member', 'Reviewer', 'Manager'])

    stateDef = workflow.states['published']
    stateDef.setProperties(title="""published""",
                           transitions=['retract', 'restricted_publish'])
    stateDef.setPermission('Access contents information',
                           1,
                           ['Anonymous', 'Reviewer', 'Manager'])
    stateDef.setPermission('View',
                           1,
                           ['Anonymous', 'Reviewer', 'Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Reviewer', 'Manager'])
    stateDef.setPermission('List folder contents',
                           1,
                           ['Anonymous', 'Reviewer', 'Manager'])

    stateDef = workflow.states['pending']
    stateDef.setProperties(title="""pending""",
                           transitions=['retract2', 'publish', 'reject'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Owner', 'Author', 'Reviewer', 'Manager'])
    stateDef.setPermission('View',
                           0,
                           ['Owner', 'Author', 'Reviewer', 'Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Reviewer', 'Manager'])
    stateDef.setPermission('List folder contents',
                           0,
                           ['Owner', 'Author', 'Reviewer', 'Manager'])

    stateDef = workflow.states['private']
    stateDef.setProperties(title="""private""",
                           transitions=['restricted_publish', 'publish', 'submit'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Owner', 'Author', 'Manager'])
    stateDef.setPermission('View',
                           0,
                           ['Owner', 'Author', 'Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Owner', 'Author', 'Manager'])
    stateDef.setPermission('List folder contents',
                           0,
                           ['Owner', 'Author', 'Manager'])

    ## Transitions initialization

    transitionDef = workflow.transitions['restricted_publish']
    transitionDef.setProperties(title="""restricted publish""",
                                new_state_id="""restricted""",
                                trigger_type=1,
                                script_name="",
                                after_script_name="",
                                actbox_name="""restricted publish""",
                                actbox_url="",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Owner;Reviewer;Manager'},
                                )

    transitionDef = workflow.transitions['publish']
    transitionDef.setProperties(title="""publish""",
                                new_state_id="""published""",
                                trigger_type=1,
                                script_name="",
                                after_script_name="",
                                actbox_name="""publish""",
                                actbox_url="",
                                actbox_category="""workflow""",
                                props={'guard_permissions': 'Review portal content'},
                                )

    transitionDef = workflow.transitions['retract2']
    transitionDef.setProperties(title="""Retract""",
                                new_state_id="""private""",
                                trigger_type=1,
                                script_name="",
                                after_script_name="",
                                actbox_name="""Retract""",
                                actbox_url="",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Owner;Author;Manager'},
                                )

    transitionDef = workflow.transitions['retract']
    transitionDef.setProperties(title="""retract""",
                                new_state_id="""private""",
                                trigger_type=1,
                                script_name="",
                                after_script_name="",
                                actbox_name="""retract""",
                                actbox_url="",
                                actbox_category="""workflow""",
                                props={'guard_permissions': 'Review portal content'},
                                )

    transitionDef = workflow.transitions['reject']
    transitionDef.setProperties(title="""reject""",
                                new_state_id="""private""",
                                trigger_type=1,
                                script_name="",
                                after_script_name="",
                                actbox_name="""reject""",
                                actbox_url="",
                                actbox_category="""workflow""",
                                props={'guard_permissions': 'Review portal content'},
                                )

    transitionDef = workflow.transitions['submit']
    transitionDef.setProperties(title="""submit""",
                                new_state_id="""pending""",
                                trigger_type=1,
                                script_name="",
                                after_script_name="",
                                actbox_name="""submit""",
                                actbox_url="",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Owner;Author;Manager'},
                                )

    ## State Variable
    workflow.variables.setStateVar('review_state')

    ## Variables initialization
    variableDef = workflow.variables['review_history']
    variableDef.setProperties(description="""Provides access to workflow history""",
                              default_value="",
                              default_expr="""state_change/getHistory""",
                              for_catalog=0,
                              for_status=0,
                              update_always=0,
                              props={'guard_permissions': 'Request review; Review portal content'})

    variableDef = workflow.variables['comments']
    variableDef.setProperties(description="""Comments about the last transition""",
                              default_value="",
                              default_expr="""python:state_change.kwargs.get('comment', '')""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['time']
    variableDef.setProperties(description="""Time of the last transition""",
                              default_value="",
                              default_expr="""state_change/getDateTime""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['actor']
    variableDef.setProperties(description="""The ID of the user who performed the last transition""",
                              default_value="",
                              default_expr="""user/getId""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['action']
    variableDef.setProperties(description="""The last transition""",
                              default_value="",
                              default_expr="""transition/getId|nothing""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    ## Worklists Initialization

    worklistDef = workflow.worklists['my_workflow']
    worklistStates = ['pending']
    actbox_url = "%(portal_url)s/search?review_state=" + "&review_state=".join(worklistStates)
    worklistDef.setProperties(description="Reviewer tasks",
                              actbox_name="Pending (%(count)d)",
                              actbox_url=actbox_url,
                              actbox_category="global",
                              props={'guard_permissions': 'Review portal content',
                                     'guard_roles': '',
                                     'var_match_review_state': ';'.join(worklistStates)})


def createminaraad_folder_workflow(self, id):
    """Create the workflow for minaraad.
    """

    ob = DCWorkflowDefinition(id)
    setupminaraad_folder_workflow(self, ob)
    return ob


addWorkflowFactory(createminaraad_folder_workflow,
                   id='minaraad_folder_workflow',
                   title='minaraad_folder_workflow')
