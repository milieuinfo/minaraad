from Products.minaraad.config import *
from sets import Set
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import addDirectoryViews
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

out = StringIO()

def install(self):
    
    _configurePortalProps(self)
    
    out.write("Create folder structure")
    createFolderStructure(self)
    
    out.write("Setting the workflow")
    # _setWorkflow(self, out)
    
    out.write("Add member data properties.")
    addMemberDataProperties(self, out)
    deactivateAreaCreations(self, out)
    changeCookieTimeOut(self, out)
    
    setupMinaraadProperties(self, out)

    out.write("Add configlets")
    addConfiglets(self, out)
    
    print >> out, "Resetting portal root's allowed types"
    _resetPloneRootAllowedTypes(self)
    
    print >> out, "Disallowing globally disallowed types"
    _resetAddableTypes(self)
    
    print >> out, "Restricting locally allowed types"
    _restrictLocallyAllowedTypes(self)
    
    print >> out, "Adding extra folder views"
    _addExtraViews(self)
    
    print >> out, "Setting specific views on certain folders"
    _setViews(self)
    
    return out.getvalue()

def _configurePortalProps(portal):
    """Customize the portal properties.

    This method changes the right and left slots on the portal folder
    and customizes the navtree properties by omitting all IDs from
    IDS_NOT_TO_LIST.
    """

    print >> out, "Customizing portal properties"
    # customize slots - add the slots to the portal folder
    portal._updateProperty('left_slots', LEFT_SLOTS)

    # portal title
    portal._updateProperty('title',PORTAL_TITLE)
    #Email information
    portal._updateProperty('email_from_address', EMAIL_FROM_ADDRESS)
    portal._updateProperty('email_from_name', EMAIL_FROM_NAME)

    # customize navtree properties - idsNotToList
    props_tool = getToolByName(portal, 'portal_properties')
    props_tool.navtree_properties._updateProperty('idsNotToList',
                                                  tuple(IDS_NOT_TO_LIST))
                                                  
    # customize navtree_properties - metaTypesNotToList
    types_tool = getToolByName(portal, 'portal_types')
    types = types_tool.listContentTypes()
    metaTypesNotToList = [type_ for type_ in types 
                          if type_ not in TYPES_TO_LIST]
    props_tool.navtree_properties._updateProperty('metaTypesNotToList',
                                                  tuple(metaTypesNotToList))

def createFolderStructure(portal):
    """Create the initial folders in the root of the portal
    """
    # first of all let's remove the object we don't want in the portal root
    itemsToRemove = ['news', 'events','Members']
    for item in itemsToRemove:
        if hasattr( portal, item): 
            portal._delObject(item)
    # Now let's create the ones we want
    for node in ROOT_CHILDREN:
        if node['id'] not in portal.objectIds():
            createNode(portal, node)

def createNode(self, item):
    workflow_tool = getToolByName(self, 'portal_workflow')
    id = item['id']
    type = item['type']

    if not id in self.objectIds():
        self.invokeFactory(type, id = id)

    created_object = self._getOb(id, None)
    created_object.setTitle(item['title'])

    workflow_tool.doActionFor(created_object, 'publish')

    for child in item['children']:
        createNode(created_object, child)

def _addExtraViews(portal):
    ttool = getToolByName(portal, 'portal_types')
    for portal_type in EXTRA_VIEWS.keys():
        type_ = ttool._getOb(portal_type)
        view_methods = list(type_.view_methods)
        for view in EXTRA_VIEWS[portal_type]:
            if not view in view_methods:
                view_methods.append(view)
        type_.view_methods = tuple(view_methods)

def _setViews(portal):
    """Select different views for certain folders.
    """
    
    for location in SELECT_VIEWS:
        try:
            folder = portal
            for foldername in location.split('/'):
                if foldername:
                    folder = folder[foldername]
            folder._setPropValue('layout', SELECT_VIEWS[location])
        except:
            out.write("can't set view on %s\n" % location)

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
        ('firstname', 'string'), ('bus', 'string'),
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
            'minaraad themes', # Title of your Product
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
            'Subscriptions', # Title of your Product
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
        portal_controlpanel.registerConfiglet(
            'Subscribers', #id of your Tool
            'subscribers overview', # Title of your Product
            'string:${portal_url}/subscribers_config.html',
            'python:True', # a condition
            'Manage Portal', # access permission
            'Products', # section to which the configlet should be added: (Plone,Products,Members)
            1, # visibility
            'SubscribersID',
            'site_icon.gif', # icon in control_panel
            'Configuration for tool Subscribers.',
            None,
        )
def _resetPloneRootAllowedTypes(portal):
    """Reset the portal root's allowed types to the defaults

    (Before messing with it)
    """

    types_tool = getToolByName(portal, 'portal_types')
    portalType = types_tool._getOb('Plone Site')
    allowedTypes = []
    for type_ in types_tool.listContentTypes():
        if types_tool._getOb(type_).global_allow:
            allowedTypes.append(type_)
    portalType._setPropValue('filter_content_types', 1)
    portalType._setPropValue('allowed_content_types',
                             tuple(allowedTypes))

def _resetAddableTypes(portal):
    """Disallow certain types and allow others.
    """

    types_tool = getToolByName(portal, 'portal_types')
    folderishTypes = MINARAAD_FOLDER_WORKFLOW_TYPES
    folderishTypes.append('Plone Site')

    # Restrict plone site root
    for typeName in ['Plone Site']:
        type_ = types_tool._getOb(typeName)
        allowedTypes = [item for item in
                        list(type_.allowed_content_types)
                        if item not in GLOBAL_DISALLOW]
        type_._setPropValue('allowed_content_types',
                            tuple(allowedTypes))
    # Unrestrict folderish types
    for typeName in folderishTypes:
        type_ = types_tool._getOb(typeName)
        restriction = list(type_.allowed_content_types)
        for allowThisType in ADD_LIST:
            if not allowThisType in restriction:
                restriction.append(allowThisType)
                out.write("Allowing %s on %s.\n" %
                          (allowThisType, typeName))
        type_._setPropValue('allowed_content_types',
                            tuple(restriction))
    # Set add list
    for typeName in folderishTypes:
        catalog = portal.portal_catalog
        type_brains = catalog(Type=typeName)
        for type_brain in type_brains:
            try:
                obj = type_brain.getObject()
                obj.setConstrainTypesMode(1)
                obj.setLocallyAllowedTypes(tuple(ADD_LIST))
                obj.setImmediatelyAddableTypes(tuple(ADD_LIST))
            except:
                out.write("Error when setting addable types"
                          " on %s.\n" % typeName)

def _restrictLocallyAllowedTypes(portal):
    """
    """

    for foldername in LOCAL_ADDITIONS:
        try:
            folder = portal
            for folderitem in foldername.split('/'):
                folder = folder[folderitem]
            localAddition = LOCAL_ADDITIONS[foldername]
            if localAddition:
                restriction = ADD_LIST + localAddition
            else:
                # Special case, we don't want anything.
                # Useful for archive folders.
                restriction = []
            folder.setConstrainTypesMode(1)
            folder.setLocallyAllowedTypes(restriction)
            folder.setImmediatelyAddableTypes(restriction)
        except:
            out.write("can't set restriction on %s\n" % foldername)

def uninstall(self):
    out = StringIO()

    return out.getvalue()