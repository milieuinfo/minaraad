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

    workflow.setProperties(title='minaraad_workflow')

    ##code-section create-workflow-setup-method-header #fill in your manual code here
    ##/code-section create-workflow-setup-method-header


    for s in ['pending_from_private', 'published', 'revisioning', 'pending_from_revisioning', 'archived', 'private']:
        workflow.states.addState(s)

    for t in ['unarchive', 'submit', 'publish', 'reject', 'retract', 'archive', 'revise']:
        workflow.transitions.addTransition(t)

    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        workflow.variables.addVariable(v)

    workflow.addManagedPermission('Access contents information')
    workflow.addManagedPermission('View')
    workflow.addManagedPermission('Modify portal content')
    workflow.addManagedPermission('Change portal events')

    for l in ['second_reviewer_queue', 'reviewer_queue']:
        if not l in workflow.worklists.objectValues():
            workflow.worklists.addWorklist(l)

    ## Initial State

    workflow.states.setInitialState('private')

    ## States initialization

    stateDef = workflow.states['pending_from_private']
    stateDef.setProperties(title="""pending_from_private""",
                           transitions=['publish', 'retract'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Owner', 'Manager', 'Reviewer'])
    stateDef.setPermission('View',
                           0,
                           ['Owner', 'Manager', 'Reviewer'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager', 'Reviewer'])
    stateDef.setPermission('Change portal events',
                           0,
                           ['Manager', 'Reviewer'])

    stateDef = workflow.states['published']
    stateDef.setProperties(title="""published""",
                           transitions=['revise', 'reject', 'archive'])
    stateDef.setPermission('View',
                           1,
                           ['Anonymous', 'Manager'])
    stateDef.setPermission('Access contents information',
                           1,
                           ['Anonymous', 'Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager'])
    stateDef.setPermission('Change portal events',
                           0,
                           ['Manager'])

    stateDef = workflow.states['revisioning']
    stateDef.setProperties(title="""revisioning""",
                           transitions=['submit', 'publish'])
    stateDef.setPermission('Access contents information',
                           1,
                           ['Anonymous', 'Manager', 'Reviewer'])
    stateDef.setPermission('View',
                           1,
                           ['Anonymous', 'Manager', 'Reviewer'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('Change portal events',
                           0,
                           ['Manager', 'Owner'])

    stateDef = workflow.states['pending_from_revisioning']
    stateDef.setProperties(title="""pending_from_revisioning""",
                           transitions=['publish', 'retract'])
    stateDef.setPermission('Access contents information',
                           1,
                           ['Owner', 'Manager', 'Reviewer'])
    stateDef.setPermission('View',
                           1,
                           ['Owner', 'Manager', 'Reviewer'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager', 'Reviewer'])
    stateDef.setPermission('Change portal events',
                           0,
                           ['Manager', 'Reviewer'])

    stateDef = workflow.states['archived']
    stateDef.setProperties(title="""archived""",
                           transitions=['unarchive'])
    stateDef.setPermission('Access contents information',
                           1,
                           ['Anonymous', 'Manager'])
    stateDef.setPermission('View',
                           1,
                           ['Anonymous', 'Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager'])
    stateDef.setPermission('Change portal events',
                           0,
                           ['Manager'])

    stateDef = workflow.states['private']
    stateDef.setProperties(title="""private""",
                           transitions=['submit', 'publish'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Owner', 'Manager'])
    stateDef.setPermission('View',
                           0,
                           ['Owner', 'Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Owner', 'Manager'])
    stateDef.setPermission('Change portal events',
                           0,
                           ['Owner', 'Manager'])

    ## Transitions initialization

    transitionDef = workflow.transitions['unarchive']
    transitionDef.setProperties(title="""unarchive""",
                                new_state_id="""published""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""unarchive""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
                                )

    transitionDef = workflow.transitions['submit']
    transitionDef.setProperties(title="""submit""",
                                new_state_id="""pending_from_private""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""submit""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
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
                                props={},
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
                                props={},
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
                                props={},
                                )

    transitionDef = workflow.transitions['archive']
    transitionDef.setProperties(title="""archive""",
                                new_state_id="""archived""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""archive""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
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
                                props={},
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

    worklistDef = workflow.worklists['second_reviewer_queue']
    worklistStates = ['pending_from_revisioning']
    actbox_url = "%(portal_url)s/search?review_state=" + "&review_state=".join(worklistStates)
    worklistDef.setProperties(description="Reviewer tasks",
                              actbox_name="Pending (%(count)d)",
                              actbox_url=actbox_url,
                              actbox_category="global",
                              props={'guard_permissions': 'Review portal content',
                                     'guard_roles': '',
                                     'var_match_review_state': ';'.join(worklistStates)})
    worklistDef = workflow.worklists['reviewer_queue']
    worklistStates = ['pending_from_private']
    actbox_url = "%(portal_url)s/search?review_state=" + "&review_state=".join(worklistStates)
    worklistDef.setProperties(description="Reviewer tasks",
                              actbox_name="Pending (%(count)d)",
                              actbox_url=actbox_url,
                              actbox_category="global",
                              props={'guard_permissions': 'Review portal content',
                                     'guard_roles': '',
                                     'var_match_review_state': ';'.join(worklistStates)})

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

