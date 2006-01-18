from Products.CMFCore.utils import getToolByName
from Products.ExternalMethod.ExternalMethod import ExternalMethod

def installWorkflows(self, package, out):
    """
    """
    
    productname = 'xxx_name_this'
    workflowTool = getToolByName(self, 'portal_workflow')
    
    ourProductWorkflow = ExternalMethod('temp',
                         'temp',
                         productname+'.'+'milieudefensie_workflow',
                         'createmilieudefensie_workflow') 
    workflow = ourProductWorkflow(self, 'milieudefensie_workflow')
    workflowTool._setObject('milieudefensie_workflow', workflow)
    workflowTool.setChainForPortalTypes(['WorkflowStub'], workflow.getId())
    
    return workflowTool
