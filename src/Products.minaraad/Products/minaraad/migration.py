import logging

from Products.CMFCore.utils import getToolByName
from persistent.list import PersistentList

from Products.minaraad.themes import ThemeManager
from Products.minaraad.subscriptions import SubscriptionManager
from Products.minaraad.content.interfaces import IThemes, IUseContact
from Products.minaraad.interfaces import IAttendeeManager
from Products.minaraad.events import save_theme_name

logger = logging.getLogger('Products.minaraad.migrations')
# The default profile id of your package:
PROFILE_ID = 'profile-Products.minaraad:default'


def _migrate_themes(context, new_themes, mapping):
    manager = ThemeManager(context)
    theme_ids = [x[0] for x in manager.themes]
    # The first step is to create the new themes.
    for theme_id, value in new_themes.items():
        if theme_id in theme_ids:
            continue

        manager.addTheme(value, theme_id)

    # Now we update all objects having themes.
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog.searchResults()

    obj_count = 0
    updated_obj_count = 0
    unmapped_obj_count = 0

    for brain in brains:
        try:
            obj = brain.getObject()
        except:
            logger.info('Could not wake brain at %s' % brain.getURL())
            continue

        if not IThemes.providedBy(obj):
            continue

        obj_count += 1
        theme_id = obj.getTheme()

        if theme_id is None:
            continue

        new_id = mapping.get(theme_id, None)
        if new_id:
            obj.setTheme(new_id)
            updated_obj_count += 1
        else:
            unmapped_obj_count += 1

    # We update member's subscriptions
    mtool = getToolByName(context, 'portal_membership')
    smanager = SubscriptionManager(context)

    for user_id in mtool.listMemberIds():
        user = mtool.getMemberById(user_id)

        user_themes = []
        for th_id in smanager._getThemes(user):
            try:
                th_id = int(th_id)
            except ValueError:
                continue

            if th_id in new_themes.keys():
                # This one was already migrated.
                user_themes.append(str(th_id))
                continue

            user_themes.append(str(mapping.get(th_id, th_id)))

        smanager._setThemes(user_themes, user)

    # Then we remove the old themes.
    manager.deleteThemes(mapping.keys())

    logger.info('Found %s objects to update: %s updated and %s without mapping' % (
        obj_count, updated_obj_count, unmapped_obj_count))

def migrate_themes(context):
    """ Updates themes.
    """
    new_themes = {40: 'Biodiversiteit',
                  41: 'Deugdelijk bestuur',
                  42: 'Omgevingskwaliteit'}

    mapping = {25: 40, 22: 41, 21: 41, 27: 41,
               32: 42, 26: 42, 24: 42}

    _migrate_themes(context, new_themes, mapping)

def save_object_themes(context):
    """ Manually triggers the 'save_theme_name' event
    for all concerned objects.
    """
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog.searchResults()

    obj_count = 0

    logger.info('Found %s objects' % len(brains))
    for brain in brains:
        try:
            obj = brain.getObject()
        except:
            logger.info('Could not wake brain at %s' % brain.getURL())
            continue

        if not IThemes.providedBy(obj):
            continue

        save_theme_name(obj, None)
        obj_count += 1

    logger.info('Migrated %s objects' % obj_count)

def migrate_contacts(context):
    """ Split the contact field into Coordinator and Authors field.
    """
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog.searchResults()

    obj_count = 0
    coordinator_count = 0
    authors_count = 0

    logger.info('Found %s objects' % len(brains))
    for brain in brains:
        try:
            obj = brain.getObject()
        except:
            logger.info('Could not wake brain at %s' % brain.getURL())
            continue

        if not IUseContact.providedBy(obj):
            continue

        obj_count += 1
        contacts = obj.getContact()

        if len(contacts) == 0:
            continue

        coordinator_count += 1
        obj.setCoordinator(contacts[0])

        if len(contacts) > 1:
            obj.setAuthors(contacts[1:])
            authors_count += 1

        obj.setContact([])

    logger.info('Migrated %s objects: %s with  a coordinator and %s with authors' % (
        obj_count, coordinator_count, authors_count))


def update_controlpanel(context):
    context.runImportStepFromProfile(PROFILE_ID, 'controlpanel')
    context.runImportStepFromProfile(PROFILE_ID, 'action-icons')


def update_portal_types(context):
    context.runImportStepFromProfile(PROFILE_ID, 'typeinfo')


def apply_workflow_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'workflow')
    # Run the update security on the workflow tool.
    logger.info('Updating security settings.  This may take a while...')
    wf_tool = getToolByName(context, 'portal_workflow')
    wf_tool.updateRoleMappings()
    logger.info('Done updating security settings.')


def apply_properties_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'properties')

def remove_double_subscriptions(context):
    """ Update _attendees object to use PersistenList
    and remove double attendees.
    """
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog.searchResults(portal_type = ['Hearing', 'MREvent'])

    obj_count = 0
    double_count = 0

    for brain in brains:
        try:
            obj = brain.getObject()
        except:
            logger.warning('Could not wake object at: %s' % brain.getURL())
            continue

        adapter = IAttendeeManager(obj)
        attendees = adapter.attendees()

        new_attendees = PersistentList()
        double_found = False

        for att in attendees:
            if att in new_attendees:
                double_found = True
                continue

            new_attendees.append(att)

        obj._attendees = new_attendees
        if double_found:
            double_count += 1

        obj.restrictedTraverse('@@attendees_view').groupedAttendees()
        obj_count += 1


    logger.info('Updated %s objects with PersistentList, found %s objects with double attendees' % (
        obj_count, double_count))


def to_plone41(context):
    # This applies the plone41 profile from minaraad.  This has some
    # steps that should only be applied once, during the upgrade to
    # Plone 4.1.
    profile_id = 'profile-Products.minaraad:plone41'
    context.runAllImportStepsFromProfile(profile_id, purge_old=False)

def apply_gs_step(context, step):
    context.runImportStepFromProfile(PROFILE_ID, step)

def apply_actions(context):
    apply_gs_step(context, 'actions')

def apply_component_registry(context):
    apply_gs_step(context, 'componentregistry')

def apply_css_registry(context):
    apply_gs_step(context, 'cssregistry')

def apply_skins(context):
    apply_gs_step(context, 'skins')

def apply_portlets(context):
    apply_gs_step(context, 'portlets')

def apply_viewlets(context):
    apply_gs_step(context, 'viewlets')

def install_emaillogin(context):
    profile_id = 'profile-collective.emaillogin4:default'
    context.runAllImportStepsFromProfile(profile_id, purge_old=False)
