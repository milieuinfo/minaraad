from Products.minaraad.config import *
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.transforms.lynx_dump import lynx_dump
from Products.RichDocument.Extensions.utils import \
    registerAttachmentsFormControllerActions
from StringIO import StringIO
from Products.DCWorkflow.DCWorkflow import WorkflowException

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
    _setWorkflow(self, out)

    out.write("Add member data properties.")
    addMemberDataProperties(self, out)
    deactivateAreaCreations(self, out)
    changeCookieTimeOut(self, out)

    setupMinaraadProperties(self, out)

    out.write("Add configlets")
    addThemesConfiglets(self, out)
    addServiceConfiglet(self, out)

    out.write("Mailhost")
    configureMailHost(self)

    _disableControlPanelActions(self)

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

    print >> out, "Make FCKeditor the default for all members"
    _configureFCKeditor(self)

    # Set up form controller actions for the widgets to work
    registerAttachmentsFormControllerActions(self)
    print >> out, "Added actions for the attachment controls to the base_edit form controller."

    _addLynxDumpTransform(self)
    print >> out, "added lynx_dump transform"

    _switchOffUnwantedActions(self)
    print >> out, "Switched off unwanted actions"

    _switchOnActions(self)
    print >> out, "Switch on our actions"

    _addTextIndexNG3Index(self, out)

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
    portal._updateProperty('right_slots', RIGHT_SLOTS)
    # Set validate_email on so always an e-mail is sent when a new
    # member registrates
    portal._updateProperty('validate_email', 1)

    # portal title
    portal._updateProperty('title', PORTAL_TITLE)
    #Email information
    portal._updateProperty('email_from_address', EMAIL_FROM_ADDRESS)
    portal._updateProperty('email_from_name', EMAIL_FROM_NAME)
    #Setting dateformat
    props = portal.portal_properties.site_properties
    props._updateProperty('localTimeFormat', LOCAL_TIME_FORMAT)
    props._updateProperty('localLongTimeFormat', LOCAL_LONG_TIME_FORMAT)
    props._updateProperty('default_language', DEFAULT_LANGUAGE)

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

    # New navtree_property - titlesNotInTabs
    navtree_props = props_tool.navtree_properties
    if not navtree_props.hasProperty('titlesNotInTabs'):
        navtree_props.manage_addProperty('titlesNotInTabs',
                                         TITLES_NOT_IN_TABS, 'lines')


def createFolderStructure(portal):
    """Create the initial folders in the root of the portal
    """
    # first of all let's remove the object we don't want in the portal root
    itemsToRemove = ['news', 'events', 'Members']
    for item in itemsToRemove:
        if hasattr(portal, item):
            portal._delObject(item)
    # Now let's create the ones we want
    for node in ROOT_CHILDREN:
        #if node['id'] not in portal.objectIds():
        createNode(portal, node)


def createNode(self, item):
    workflow_tool = getToolByName(self, 'portal_workflow')
    id = item['id']
    type = item['type']

    if not id in self.objectIds():
        self.invokeFactory(type, id = id)

    created_object = self._getOb(id, None)
    created_object.setTitle(item['title'])

    try:
        workflow_tool.doActionFor(created_object, 'publish')
    except WorkflowException, e:
        pass

    for child in item['children']:
        createNode(created_object, child)


def _switchOffUnwantedActions(portal):
    """Switch off unwanted actions (portal_actions)

    This method switchs off some unwanted actions
    in a standard out-of-the-box Plone site
    (these actions can be found in portal_actions).
    """

    st = getToolByName(portal, 'portal_actions')
    st_actions = st._cloneActions()
    for action in st_actions:
        if action.id in INVISIBLE_ACTIONS:
            if action.visible:
                print >> out, "Switching off unwanted action %s." % action.id
                action.visible = 0
    st._actions = st_actions


def _switchOnActions(portal):
    """Switch on wanted actions(portal_actions)
    """
    tab = getToolByName(portal, 'portal_actions')
    tab_actions = tab._cloneActions()
    actionDefined = 0
    actionContactDefined = 0
    for a in tab_actions:
        if a.id == 'sitemap':
            a.title = 'Sitemap'
            a.visible = 1
        if a.id in ['mina_library']:
            a.visible = 1
            actionDefined = 1
        if a.id == 'contactpersonen':
            a.visible = 1
            actionContactDefined = 1
        tab._actions = tab_actions
    if actionDefined == 0:
        tab.addAction('mina_library',
                      'Bibliotheek',
                      'string:$portal_url/mina_library',
                      '',
                      'View',
                      'site_actions')
    if actionContactDefined == 0:
        tab.addAction('contactpersonen',
                      'Contactpersonen',
                      'string:$portal_url/contactpersonen',
                      '',
                      'Manage portal',
                      'user')


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
                {'id': 'themes', 'type': 'lines', 'mode': 'w'},
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
    print >> out, "Setting MiNa-Raad workflow"
    workflowTool = getToolByName(portal, 'portal_workflow')

    workflowTool.setDefaultChain('minaraad_workflow')
    workflowTool.setChainForPortalTypes(
        ['Folder', 'Large Plone Folder', 'Topic'],
        'minaraad_folder_workflow')
    workflowTool.setChainForPortalTypes(['Image', 'File'], 'minaraad_workflow')
    workflowTool.updateRoleMappings()

    portal.manage_permission('Add portal content',
                             ['Author', 'Owner', 'Manager'], 1)
    portal.manage_permission('ATContentTypes: Add File', ['Author'], 1)
    portal.manage_permission('ATContentTypes: Add Folder', ['Author'], 1)
    portal.manage_permission('Delete objects', ['Owner', 'Manager'], 1)
    portal.manage_permission('Add portal folders',
                             ['Author', 'Owner', 'Manager'], 1)
    portal.manage_permission('List folder contents',
                             ['Author', 'Owner', 'Manager'], 1)
    portal.manage_permission('Manage properties',
                             ['Author', 'Owner', 'Manager'], 1)
    portal.manage_permission('Undo changes', ['Owner', 'Manager'], 1)


def addMemberDataProperties(self, out):
    """Added extra Memberdata information to the memberdata tool
    """
    memberdata = getToolByName(self, 'portal_memberdata')

    add_properties = (
        ('company', 'string'), ('jobtitle', 'string'),
        ('street', 'string'), ('housenumber', 'string'),
        ('zipcode', 'string'), ('city', 'string'),
        ('firstname', 'string'), ('bus', 'string'),
        ('phonenumber', 'string'), ('subscriptions', 'lines'),
    )

    add_properties = [x for x in add_properties
                      if x[0] not in memberdata.propertyIds()]
    for p, pType in add_properties:
        memberdata.manage_addProperty(p, '', pType)
        print >> out, "Property %r added to memberdata." % p

    # special care for our selection property gender
    if 'genders' not in memberdata.propertyIds():
        memberdata.manage_addProperty('genders', TITLE_VOCAB, 'lines')

    if 'gender' not in memberdata.propertyIds():
        memberdata.manage_addProperty('gender', 'genders', 'selection')

    # adding Country
    countries = ['Belgie', 'Nederland', 'Ander land']

    if 'country' not in memberdata.propertyIds():
        memberdata.manage_addProperty('select_country', countries, 'lines')
        memberdata.manage_addProperty('country', 'select_country', 'selection')

    # adding last_modification_date
    if 'last_modification_date' not in memberdata.propertyIds():
        memberdata.manage_addProperty('last_modification_date', '2000/01/01',
                                      'date')


def addThemesConfiglets(self, out):
    # register tools as configlets
    portal_controlpanel = getToolByName(self, 'portal_controlpanel')
    configlets = portal_controlpanel.enumConfiglets(group='Products')
    installed = False
    for configlet in configlets:
        if configlet['id'] == 'Themes':
            installed = True

    if not installed:
        portal_controlpanel.registerConfiglet(
            'Themes', #id of your Tool
            'minaraad themes', # Title of this configlet
            'string:${portal_url}/minaraad_config.html',
            'python:True', # a condition
            'Manage Portal', # access permission
            'Products', # section to which the configlet should be
                        # added: (Plone, Products, Members)
            1, # visibility
            'ThemesID', # Application id
            'site_icon.gif', # icon in control_panel
            'Configuration for Minaraad properties.',
            None,
        )
        portal_controlpanel.registerConfiglet(
            'Subscriptions', #id of your Tool
            'Subscriptions', # Title of this configlet
            'string:${portal_url}/subscriptions_config.html',
            'python:True', # a condition
            'View', # access permission
            'Member', # section to which the configlet should be
                      # added: (Plone, Products, Members)
            1, # visibility
            'SubscriptionsID', # Application id
            'site_icon.gif', # icon in control_panel
            'Configuration for tool Subscriptions.',
            None,
        )
        portal_controlpanel.registerConfiglet(
            'Subscribers', #id of your Tool
            'subscribers overview', # Title of this configlet
            'string:${portal_url}/subscribers_config.html',
            'python:True', # a condition
            'Manage Portal', # access permission
            'Products', # section to which the configlet should be
                        # added: (Plone, Products, Members)
            1, # visibility
            'SubscribersID', # Application id
            'site_icon.gif', # icon in control_panel
            'Configuration for tool Subscribers.',
            None,
        )


def addServiceConfiglet(self, out):
    portal_controlpanel = getToolByName(self, 'portal_controlpanel')
    configlets = portal_controlpanel.enumConfiglets(group='Products')
    installed = False
    for configlet in configlets:
        if configlet['id'] == 'minaraad_service':
            installed = True

    if not installed:
        portal_controlpanel.registerConfiglet(
            'minaraad_service', #id of your Tool
            'Servicepaneel Minaraad', # Title of this configlet
            'string:${portal_url}/minaraad_service',
            'python:True', # a condition
            'Manage Portal', # access permission
            'Products', # section to which the configlet should be
                        # added: (Plone, Products, Members)
            1, # visibility
            'minaraad', # Application id
            'site_icon.gif', # icon in control_panel
            'Servicepaneel voor Minaraad.',
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

    for type_ in types_tool.listContentTypes():
        if type_ in GLOBAL_DISALLOW:
            typeObj = types_tool[type_]
            typeObj._setPropValue('global_allow', 0)

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


def _configureFCKeditor(portal):
    """Update FCKEditor settings
    """
    memberdata = getToolByName(portal, 'portal_memberdata')
    props = getToolByName(portal, 'portal_properties')
    fckprops = props.fckeditor_properties

    memberdata._updateProperty('wysiwyg_editor', 'FCKeditor')
    fckprops._updateProperty('fck_default_skin', 'office2003')
    fckprops._updateProperty('fck_force_height', FCK_FORCE_HEIGHT)
    fckprops._updateProperty('fck_force_width', FCK_FORCE_WIDTH)
    fckprops._updateProperty('fck_toolbar', FCK_TOOLBAR)
    fckprops._updateProperty('fck_custom_toolbar', FCK_CUSTOM_TOOLBAR)
    fckprops._updateProperty('fck_area_style', FCK_AREA_STYLE)
    fckprops._updateProperty('fck_menu_styles', FCK_MENU_STYLES)

    # disable the member prefs, has bugs
    control = getToolByName(portal, 'portal_controlpanel')
    actions = control._cloneActions()
    for action in actions:
        if action.id == 'fckeditor_member_prefs':
            action.visible = 0
            print >> out, "Switching off unwanted action %s." % action.id
    control._actions = actions


def _addLynxDumpTransform(portal):
    transforms = portal.portal_transforms
    transforms.registerTransform(lynx_dump())


def _addTextIndexNG3Index(portal, out):
    """Remove the standard SearchableText index
    """
    catalog_tool = getToolByName(portal, 'portal_catalog')
    if (str(type(catalog_tool._catalog.getIndex('SearchableText').aq_base)) ==
        "<class 'Products.TextIndexNG3.TextIndexNG3.TextIndexNG3'>"):
        return

    print >> out, "Removing SearchableText index"

    catalog_tool._removeIndex('SearchableText')

    print >> out, "Adding new index for TextIndexNG3"
    catalog_tool.manage_addIndex(
        'SearchableText',
        'TextIndexNG3',
        extra=dict(default_encoding='utf-8',
                   use_converters=1,
##                    query_parser='txng.parsers.dumb_and',
                   languages=('en', 'nl', ''),
                   )
        )
    catalog_tool.manage_reindexIndex('SearchableText')


def _disableControlPanelActions(portal):
    """Disable some actions defined in portal_controlpanel
    """

    cpanel = getToolByName(portal, 'portal_controlpanel')
    actions = cpanel._cloneActions()
    for action in actions:
        if action.id in INVISIBLE_CONTROLPANEL_ACTIONS:
            action.visible = 0
            print >> out, "Switching off unwanted action %s." % action.id
    cpanel._actions = actions


def configureMailHost(portal):
    mh = getToolByName(portal, 'MailHost')
    mh.manage_makeChanges(title='Mail Host',
                          smtp_host=SMTP_HOST,
                          smtp_port=SMTP_PORT,
                          smtp_userid=SMTP_USERID,
                          smtp_pass=SMTP_PASS)


def uninstall(self):
    out = StringIO()
    portal_controlpanel = getToolByName(self, 'portal_controlpanel')
    portal_controlpanel.unregisterConfiglet('Themes')
    portal_controlpanel.unregisterConfiglet('Subscriptions')
    portal_controlpanel.unregisterConfiglet('Subscribers')
    return out.getvalue()
