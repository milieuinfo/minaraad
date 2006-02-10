from Products.minaraad.config import *
from sets import Set
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO

def install(self):
    out = StringIO()

    out.write("Setting the workflow")
    _setWorkflow(self, out)

    out.write("Add member data properties.")
    addMemberDataProperties(self, out)

    return out.getvalue()


def _setWorkflow(portal, out):
    print >> out, "Setting internetlayout workflow"
    workflowTool = getToolByName(portal, 'portal_workflow')
    # reset plone site (used to be set to internetworkflow...)
    currentWorkflow = workflowTool.getChainForPortalType('Plone Site')
    if currentWorkflow:
        print >> out, "Resetting workflow for Plone Site object."
        workflowTool.setChainForPortalTypes(['Plone Site'],
                                            '')
    # Now the normal stuff
    types_tool = getToolByName(portal, 'portal_types')
    # Normal workflow
    types = types_tool.listContentTypes()
    types = [type_ for type_ in types 
             if type_ not in (NOT_INTERNET_WORFKLOW_TYPES +
                              INTERNET_FOLDER_WORKFLOW_TYPES)]
    for type_ in types:
        currentWorkflow = list(workflowTool.getChainForPortalType(type_))
        if currentWorkflow != ['minaraad_workflow']:
            msg = "Setting internetlayout workflow for %s (from %s)"\
                  % (type_, currentWorkflow)
            print >> out, msg
            workflowTool.setChainForPortalTypes([type_],
                                                'minaraad_workflow')


def addMemberDataProperties(self, out):
    """Added extra Memberdata information to the memberdata tool
    """
    memberdata = getToolByName(self, 'portal_memberdata')
    
    add_properties = Set(
        ('company', 'jobtitle', 'street', 'housenumber', 
         'zipcode', 'city', 'phonenumber',))
    add_properties -= Set(memberdata.propertyIds())
    for p in add_properties:
        memberdata.manage_addProperty(p, '', 'string')
        print >> out, "Property %r added to memberdata." % p

    # special care for our selection property gender
    if 'genders' not in memberdata.propertyIds():
        memberdata.manage_addProperty('genders', ['Heer','Mevrouw'], 'lines')

    if 'gender' not in memberdata.propertyIds():
        memberdata.manage_addProperty('gender', 'genders', 'selection')
    
    # adding Country
    countries = ['Belgie', 'Nederland', 'Ander land']
    
    if 'country' not in memberdata.propertyIds():
        memberdata.manage_addProperty('select_country', countries, 'lines')
        memberdata.manage_addProperty('country', 'select_country', 'selection')
        memberdata.manage_addProperty('other_country', '', 'string')
