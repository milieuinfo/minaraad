from Products.minaraad.config import *
from sets import Set
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO

MINARAAD_PROPERTIES = 'minaraad_properties'
THEMES_PROPERTY = [
    '1/Water',
    '2/Klimaat & energie',
    '3/Afval',
    '4/Bodem',
    '5/Europa & Duurzame ontwikkeling',
    '6/Mobiliteit',
    '7/Ruimtelijke ordening',
    '8/Natuur & landbouw',
    '9/NME',
    '10/Milieubegroting',
    '11/Milieuplanning',
    '12/Milieureglementering',
    '13/Instrumenten',
]

def install(self):
    out = StringIO()

    out.write("Setting the workflow")
    # _setWorkflow(self, out)

    out.write("Add member data properties.")
    addMemberDataProperties(self, out)
    deactivateAreaCreations(self, out)
    changeCookieTimeOut(self, out)
    
    setupMinaraadProperties(self, out)

    out.write("Add configlets")
    addConfiglets(self, out)

    return out.getvalue()

def setupMinaraadProperties(self, out):
    propsTool = getToolByName(self, 'portal_properties')
    
    sheet = getattr(propsTool, MINARAAD_PROPERTIES, None)
    if sheet is None:
        propsTool.addPropertySheet(MINARAAD_PROPERTIES, 'Minaraad Properties')
        sheet = getattr(propsTool, MINARAAD_PROPERTIES)
        sheet._properties = sheet._properties + (
                {'id':'themes', 'type':'lines', 'mode':'w'},
            )

        sheet.manage_changeProperties({'themes': THEMES_PROPERTY})
        print >> out, "Added new '%s' property sheet to " \
                      "portal_properties" % MINARAAD_PROPERTIES
    else:
        print >> out, "Skipped adding '%s' property sheet to " \
                      "portal_properties since it already " \
                      "exists" % MINARAAD_PROPERTIES


def changeCookieTimeOut(self, out):
    propsTool = getToolByName(self, 'portal_properties')
    siteProperties = propsTool.site_properties
    siteProperties.manage_changeProperties({'auth_cookie_length': 30})

def deactivateAreaCreations(self, out):
    
    membership = getToolByName(self, 'portal_membership')
    if membership.getMemberareaCreationFlag():
        print >> out, "Deactiving automatic membership area creation"
        membership.setMemberareaCreationFlag()
    

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
    
    add_properties = (
        ('company', 'string'), ('jobtitle', 'string'), 
        ('street', 'string'), ('housenumber', 'string'),
        ('zipcode', 'string'), ('city', 'string'), 
        ('phonenumber','string'), ('subscriptions', 'lines'),
    )
    
    add_properties = [x for x in add_properties 
                      if x[0] not in memberdata.propertyIds()]
    for p, pType in add_properties:
        memberdata.manage_addProperty(p, '', pType)
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

def addConfiglets(self, out):
    # register tools as configlets
    portal_controlpanel = getToolByName(self,'portal_controlpanel')
    configlets = portal_controlpanel.enumConfiglets(group='Products')
    installed = False
    for configlet in configlets:
        if configlet['id'] == 'Themes':
            installed = True
        
    if not installed:
        portal_controlpanel.registerConfiglet(
            'Themes', #id of your Tool
            'minaraad', # Title of your Troduct
            'string:${portal_url}/minaraad_config.html',
            'python:True', # a condition
            'Manage Portal', # access permission
            'Products', # section to which the configlet should be added: (Plone,Products,Members)
            1, # visibility
            'ThemesID',
            'site_icon.gif', # icon in control_panel
            'Configuration for Minaraad properties.',
            None,
        )
        portal_controlpanel.registerConfiglet(
            'Subscriptions', #id of your Tool
            'Subscriptions', # Title of your Troduct
            'string:${portal_url}/subscriptions_config.html',
            'python:True', # a condition
            'View', # access permission
            'Member', # section to which the configlet should be added: (Plone,Products,Members)
            1, # visibility
            'SubscriptionsID',
            'site_icon.gif', # icon in control_panel
            'Configuration for tool Subscriptions.',
            None,
        )
