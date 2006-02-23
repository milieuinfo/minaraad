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
from Products.ExternalMethod.ExternalMethod import ExternalMethod
##code-section module-header #fill in your manual code here
##/code-section module-header


def installWorkflows(self, package, out):
    """Install the custom workflows for this product."""

    productname = 'minaraad'
    workflowTool = getToolByName(self, 'portal_workflow')

    ourProductWorkflow = ExternalMethod('temp', 'temp',
                         productname+'.'+'minaraad_workflow',
                         'createminaraad_workflow')
    workflow = ourProductWorkflow(self, 'minaraad_workflow')
    workflowTool._setObject('minaraad_workflow', workflow)
    workflowTool.setChainForPortalTypes(['WorkflowStub', 'Hearing', 'AgendaItem', 'Study'], workflow.getId())

    ourProductWorkflow = ExternalMethod('temp', 'temp',
                         productname+'.'+'minaraad_folder_workflow',
                         'createminaraad_folder_workflow')
    workflow = ourProductWorkflow(self, 'minaraad_folder_workflow')
    workflowTool._setObject('minaraad_folder_workflow', workflow)
    workflowTool.setChainForPortalTypes(['WorkflowStub'], workflow.getId())
    ##code-section after-workflow-install #fill in your manual code here
    ##/code-section after-workflow-install


    return workflowTool

def uninstallWorkflows(self, package, out):
    """Deinstall the workflows.

    This code doesn't really do anything, but you can place custom
    code here in the protected section.
    """

    ##code-section workflow-uninstall #fill in your manual code here
    ##/code-section workflow-uninstall

    pass
