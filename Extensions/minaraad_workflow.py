# File: minaraad.py
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


from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.minaraad.config import *

##code-section create-workflow-module-header #fill in your manual code here
##/code-section create-workflow-module-header


productname = 'minaraad'

def setupminaraad_workflow(self, workflow):
    """Define the minaraad_workflow workflow.
    """
    # Add additional roles to portal
    portal = getToolByName(self,'portal_url').getPortalObject()
    data = list(portal.__ac_roles__)
    for role in ['Author', 'Council Member']:
        if not role in data:
            data.append(role)
    portal.__ac_roles__ = tuple(data)

    workflow.setProperties(title='minaraad_workflow')

    ##code-section create-workflow-setup-method-header #fill in your manual code here
    ##/code-section create-workflow-setup-method-header


    for s in ['pending_private', 'published', 'pending_revisioning', 'revisioning', 'restricted', 'private']:
        workflow.states.addState(s)

    for t in ['restricted_publish', 'submit', 'publish', 'retract2', 'retract', 'reject', 'submit2', 'revise']:
        workflow.transitions.addTransition(t)

    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        workflow.variables.addVariable(v)

    workflow.addManagedPermission('edit')
    workflow.addManagedPermission('Access contents information')
    workflow.addManagedPermission('View')
    workflow.addManagedPermission('List folder contents')
    workflow.addManagedPermission('Modify portal content')
    workflow.addManagedPermission('Delete Object')
    workflow.addManagedPermission('add portal content')
    workflow.addManagedPermission('Modify folder contents')
    workflow.addManagedPermission('Add portal content')

    for l in []:
        if not l in workflow.worklists.objectValues():
            workflow.worklists.addWorklist(l)

    ## Initial State

    workflow.states.setInitialState('private')

    ## States initialization

    stateDef = workflow.states['pending_private']
    stateDef.setProperties(title="""pending_private""",
                           transitions=['publish', 'restricted_publish', 'reject', 'retract'])
    stateDef.setPermission('edit',
                           0,
                           ['Author', 'Owner', 'Reviewer', 'Manager'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Author', 'Owner', 'Reviewer', 'Manager'])
    stateDef.setPermission('View',
                           0,
                           ['Author', 'Owner', 'Reviewer', 'Manager'])
    stateDef.setPermission('List folder contents',
                           0,
                           ['Author', 'Owner', 'Reviewer', 'Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Reviewer', 'Manager'])
    stateDef.setPermission('Delete Object',
                           0,
                           ['Owner', 'Reviewer', 'Manager'])

    stateDef = workflow.states['published']
    stateDef.setProperties(title="""published""",
                           transitions=['revise', 'reject'])
    stateDef.setPermission('edit',
                           0,
                           ['Author', 'Owner', 'Reviewer', 'Manager'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Anonymous', 'Member', 'Author', 'Owner', 'Council Member', 'Reviewer', 'Manager'])
    stateDef.setPermission('View',
                           0,
                           ['Anonymous', 'Member', 'Author', 'Owner', 'Council Member', 'Reviewer', 'Manager'])
    stateDef.setPermission('List folder contents',
                           0,
                           ['Anonymous', 'Member', 'Author', 'Owner', 'Council Member', 'Reviewer', 'Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Reviewer', 'Manager'])
    stateDef.setPermission('Delete Object',
                           0,
                           ['Owner', 'Reviewer', 'Manager'])

    stateDef = workflow.states['pending_revisioning']
    stateDef.setProperties(title="""pending_revisioning""",
                           transitions=['retract2', 'publish'])
    stateDef.setPermission('edit',
                           0,
                           ['Author', 'Owner', 'Reviewer', 'Manager'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Anonymous', 'Member', 'Author', 'Owner', 'Council Member', 'Reviewer', 'Manager'])
    stateDef.setPermission('View',
                           0,
                           ['Anonymous', 'Member', 'Author', 'Owner', 'Council Member', 'Reviewer', 'Manager'])
    stateDef.setPermission('List folder contents',
                           0,
                           ['Anonymous', 'Member', 'Author', 'Owner', 'Council Member', 'Reviewer', 'Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Reviewer', 'Manager'])
    stateDef.setPermission('Delete Object',
                           0,
                           ['Owner', 'Reviewer', 'Manager'])

    stateDef = workflow.states['revisioning']
    stateDef.setProperties(title="""revisioning""",
                           transitions=['publish', 'submit2'])
    stateDef.setPermission('add portal content',
                           0,
                           ['Author', 'Owner', 'Reviewer', 'Manager'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Anonymous', 'Member', 'Author', 'Owner', 'Council Member', 'Reviewer', 'Manager'])
    stateDef.setPermission('View',
                           0,
                           ['Anonymous', 'Member', 'Author', 'Owner', 'Council Member', 'Reviewer', 'Manager'])
    stateDef.setPermission('List folder contents',
                           0,
                           ['Anonymous', 'Member', 'Author', 'Owner', 'Council Member', 'Reviewer', 'Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Owner', 'Reviewer', 'Manager'])
    stateDef.setPermission('Delete Object',
                           0,
                           ['Owner', 'Reviewer', 'Manager'])

    stateDef = workflow.states['restricted']
    stateDef.setProperties(title="""restricted""",
                           transitions=[])
    stateDef.setPermission('edit',
                           0,
                           ['Author', 'Owner', 'Reviewer', 'Manager'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Owner', 'Council Member', 'Reviewer', 'Manager'])
    stateDef.setPermission('View',
                           0,
                           ['Owner', 'Council Member', 'Reviewer', 'Manager'])
    stateDef.setPermission('List folder contents',
                           0,
                           ['Owner', 'Council Member', 'Reviewer', 'Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Owner', 'Reviewer', 'Manager'])
    stateDef.setPermission('Delete Object',
                           0,
                           ['Owner', 'Reviewer', 'Manager'])

    stateDef = workflow.states['private']
    stateDef.setProperties(title="""private""",
                           transitions=['submit', 'publish'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Author', 'Owner', 'Manager'])
    stateDef.setPermission('Delete Object',
                           0,
                           ['Author', 'Owner', 'Manager'])
    stateDef.setPermission('List folder contents',
                           0,
                           ['Author', 'Owner', 'Manager'])
    stateDef.setPermission('Modify folder contents',
                           0,
                           ['Author', 'Owner', 'Manager'])
    stateDef.setPermission('View',
                           0,
                           ['Author', 'Owner', 'Manager'])
    stateDef.setPermission('Add portal content',
                           0,
                           ['Author', 'Owner', 'Manager'])
    stateDef.setPermission('edit',
                           0,
                           ['Author', 'Owner', 'Manager'])

    ## Transitions initialization

    transitionDef = workflow.transitions['restricted_publish']
    transitionDef.setProperties(title="""restricted_publish""",
                                new_state_id="""restricted""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""restricted_publish""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Reviewer;Manager'},
                                )

    transitionDef = workflow.transitions['submit']
    transitionDef.setProperties(title="""submit""",
                                new_state_id="""pending_private""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""submit""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Owner'},
                                )

    transitionDef = workflow.transitions['publish']
    transitionDef.setProperties(title="""publish""",
                                new_state_id="""published""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""publish""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Reviewer;Manager'},
                                )

    transitionDef = workflow.transitions['retract2']
    transitionDef.setProperties(title="""retract2""",
                                new_state_id="""revisioning""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""retract2""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Reviewer;Manager;Owner'},
                                )

    transitionDef = workflow.transitions['retract']
    transitionDef.setProperties(title="""retract""",
                                new_state_id="""private""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""retract""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Reviewer;Owner;Manager'},
                                )

    transitionDef = workflow.transitions['reject']
    transitionDef.setProperties(title="""reject""",
                                new_state_id="""private""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""reject""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Reviewer;Manager'},
                                )

    transitionDef = workflow.transitions['submit2']
    transitionDef.setProperties(title="""submit2""",
                                new_state_id="""pending_revisioning""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""submit2""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Reviewer;Manager;Owner'},
                                )

    transitionDef = workflow.transitions['revise']
    transitionDef.setProperties(title="""revise""",
                                new_state_id="""revisioning""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""revise""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Reviewer;Manager;Owner'},
                                )

    ## State Variable
    workflow.variables.setStateVar('review_state')

    ## Variables initialization
    variableDef = workflow.variables['review_history']
    variableDef.setProperties(description="""Provides access to workflow history""",
                              default_value="""""",
                              default_expr="""state_change/getHistory""",
                              for_catalog=0,
                              for_status=0,
                              update_always=0,
                              props={'guard_permissions': 'Request review; Review portal content'})

    variableDef = workflow.variables['comments']
    variableDef.setProperties(description="""Comments about the last transition""",
                              default_value="""""",
                              default_expr="""python:state_change.kwargs.get('comment', '')""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['time']
    variableDef.setProperties(description="""Time of the last transition""",
                              default_value="""""",
                              default_expr="""state_change/getDateTime""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['actor']
    variableDef.setProperties(description="""The ID of the user who performed the last transition""",
                              default_value="""""",
                              default_expr="""user/getId""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['action']
    variableDef.setProperties(description="""The last transition""",
                              default_value="""""",
                              default_expr="""transition/getId|nothing""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    ## Worklists Initialization


    # WARNING: below protected section is deprecated.
    # Add a tagged value 'worklist' with the worklist name to your state(s) instead.

    ##code-section create-workflow-setup-method-footer #fill in your manual code here
    ##/code-section create-workflow-setup-method-footer



def createminaraad_workflow(self, id):
    """Create the workflow for minaraad.
    """

    ob = DCWorkflowDefinition(id)
    setupminaraad_workflow(self, ob)
    return ob

addWorkflowFactory(createminaraad_workflow,
                   id='minaraad_workflow',
                   title='minaraad_workflow')

##code-section create-workflow-module-footer #fill in your manual code here
##/code-section create-workflow-module-footer

