#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from Products.minaraad.subscriptions import SubscriptionManager
# from Products.minaraad.themes import ThemeManager
from persistent.list import PersistentList
from plone import api
from plone.locking.interfaces import ILockable
from Products.CMFCalendar.exceptions import ResourceLockedError
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.minaraad.content.interfaces import IThemes, IUseContact
from Products.minaraad.events import save_theme_name
from Products.minaraad.interfaces import IAttendeeManager
from Products.ZCatalog.ProgressHandler import ZLogHandler
import logging
import transaction




logger = logging.getLogger('Products.minaraad.migrations')
# The default profile id of your package:
PROFILE_ID = 'profile-Products.minaraad:default'


# def _migrate_themes(context, new_themes, mapping):
#     manager = ThemeManager(context)
#     theme_ids = [x[0] for x in manager.themes]
#     # The first step is to create the new themes.
#     for theme_id, value in new_themes.items():
#         if theme_id in theme_ids:
#             continue
#
#         manager.addTheme(value, theme_id)
#
#     # Now we update all objects having themes.
#     catalog = getToolByName(context, 'portal_catalog')
#     brains = catalog.searchResults()
#
#     obj_count = 0
#     updated_obj_count = 0
#     unmapped_obj_count = 0
#
#     for brain in brains:
#         try:
#             obj = brain.getObject()
#         except:
#             logger.info('Could not wake brain at %s' % brain.getURL())
#             continue
#
#         if not IThemes.providedBy(obj):
#             continue
#
#         obj_count += 1
#         theme_id = obj.getTheme()
#
#         if theme_id is None:
#             continue
#
#         new_id = mapping.get(theme_id, None)
#         if new_id:
#             obj.setTheme(new_id)
#             updated_obj_count += 1
#         else:
#             unmapped_obj_count += 1
#
#     # We update member's subscriptions
#     mtool = getToolByName(context, 'portal_membership')
#     smanager = SubscriptionManager(context)
#
#     for user_id in mtool.listMemberIds():
#         user = mtool.getMemberById(user_id)
#
#         user_themes = []
#         for th_id in smanager._getThemes(user):
#             try:
#                 th_id = int(th_id)
#             except ValueError:
#                 continue
#
#             if th_id in new_themes.keys():
#                 # This one was already migrated.
#                 user_themes.append(str(th_id))
#                 continue
#
#             user_themes.append(str(mapping.get(th_id, th_id)))
#
#         smanager._setThemes(user_themes, user)
#
#     # Then we remove the old themes.
#     manager.deleteThemes(mapping.keys())
#
#     logger.info('Found %s objects to update: %s updated and %s without '
#                 'mapping' % (obj_count, updated_obj_count, unmapped_obj_count))


# def migrate_themes(context):
#     """ Updates themes.
#     """
#     new_themes = {40: 'Biodiversiteit',
#                   41: 'Deugdelijk bestuur',
#                   42: 'Omgevingskwaliteit'}
#
#     mapping = {25: 40, 22: 41, 21: 41, 27: 41,
#                32: 42, 26: 42, 24: 42}
#
#     _migrate_themes(context, new_themes, mapping)


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

    logger.info('Migrated %s objects: %s with  a coordinator and %s with '
                'authors' % (obj_count, coordinator_count, authors_count))


def update_controlpanel(context):
    context.runImportStepFromProfile(PROFILE_ID, 'controlpanel')


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
    brains = catalog.searchResults(portal_type=['Hearing', 'MREvent'])

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

    logger.info('Updated %s objects with PersistentList, found %s objects '
                'with double attendees' % (obj_count, double_count))


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


def apply_javascript_registry(context):
    apply_gs_step(context, 'jsregistry')


def apply_skins(context):
    apply_gs_step(context, 'skins')


def apply_portlets(context):
    apply_gs_step(context, 'portlets')


def apply_viewlets(context):
    apply_gs_step(context, 'viewlets')


def install_emaillogin(context):
    profile_id = 'profile-collective.emaillogin4:default'
    context.runAllImportStepsFromProfile(profile_id, purge_old=False)


def cleanup_mutable_properties(context):
    """Cleanup PAS.mutable_properties.

    There are 556 users or groups in mutable_properties that do not
    exist in source_users or source_groups.  I don't know how that can
    be and how there are so much, but we should clean them up, as they
    give lots of warnings when looking at the Users and Groups control
    panel.
    """
    grouptool = getToolByName(context, 'portal_groups')
    membertool = getToolByName(context, 'portal_membership')
    pas = getToolByName(context, 'acl_users')

    user_ids = membertool.listMemberIds()
    group_ids = grouptool.listGroupIds()
    principal_ids = set(user_ids).union(set(group_ids))
    to_remove = [user_id for user_id in pas.mutable_properties._storage.keys()
                 if user_id not in principal_ids]
    logger.info("About to remove %d users from mutable_properties that have "
                "no corresponding user or group.", len(to_remove))
    for user_id in to_remove:
        pas.mutable_properties.deleteUser(user_id)
    logger.info("Removed user ids from mutable_properties: %r", to_remove)


def fix_portraits(context):
    """Fix member portraits

    It looks like every member has defaultUser.gif as member portrait.
    There are a few problems with that.

    - The new default is defaultUser.png.

    - The old gif has been moved to the plone_deprecated skin, which
      may not always be available.

    - When testing in a fresh Plone 3 site portraits are not stored
      explicitly anymore when they are the default.

    - I think most of these are from Plone 2.5, because they have a
      file path of 'CMFPlone/skins/plone_images/defaultUser.gif',
      which gives an IOError, because it does not exist in the
      plone_images directory and probably also because the base
      CMFPlone directory is not found.

    It seems wise to clean this up, otherwise looking at the author
    page or the preferences page will give an error.

    """
    mdata = getToolByName(context, 'portal_memberdata')
    portraits = mdata.portraits
    logger.info("portal_memberdata has %d portraits before cleanup.",
                len(portraits.objectIds()))
    to_remove = []
    for user_id, portrait in portraits.objectItems():
        if portrait.getId() == 'defaultUser.gif':
            to_remove.append(user_id)
    logger.info("Will remove %d defaultUser.gif portraits.", len(to_remove))
    for user_id in to_remove:
        mdata._deletePortrait(user_id)
    logger.info("portal_memberdata has %d portraits left afer cleanup.",
                len(portraits.objectIds()))

    # I found a nice method on the memberdata tool.
    logger.info("Pruning memberdata contents.")
    mdata.pruneMemberDataContents()
    logger.info("Done.")


def fix_mutable_properties_for_groups(context):
    """Not all group property sheets have isGroup=True

    This causes warning from plone.app.controlpanel when looking at
    the users list in the Users and Groups control panel:

    Skipped user without principal object: Reviewers
    Skipped user without principal object: PWC JACHT
    etcetera.
    """
    grouptool = getToolByName(context, 'portal_groups')
    group_ids = grouptool.listGroupIds()
    pas = getToolByName(context, 'acl_users')
    props = pas.mutable_properties

    for principal_id, data in props._storage.items():
        if principal_id in group_ids and not data.get('isGroup'):
            props._storage[principal_id]['isGroup'] = True
            # notify persistence machinery of change
            props._storage[principal_id] = props._storage[principal_id]
            logger.info("Mutable property sheet of group %s is now regarded "
                        "as belonging to a group.", principal_id)


def apply_propertiestool_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'propertiestool')


def update_mailhost(context, klass):
    from Products.MailHost.interfaces import IMailHost
    portal = getToolByName(context, 'portal_url').getPortalObject()
    if portal.MailHost.__class__ == klass:
        logger.info("portal.MailHost is already of class %s", klass)
        return
    sm = portal.getSiteManager()
    sm.unregisterUtility(portal.MailHost, provided=IMailHost)
    portal._delObject('MailHost')
    MailHost = klass('MailHost')
    # Note that MailHost._transactional is True by default, which
    # seems good: only send the mails when the transaction finishes.
    portal._setObject('MailHost', MailHost)
    sm.registerUtility(MailHost, provided=IMailHost)
    logger.info("Created new portal.MailHost with class %s", klass)


def update_to_maildrophost(context):
    from Products.SecureMaildropHost.SecureMaildropHost import \
        SecureMaildropHost as klass
    update_mailhost(context, klass)


def restore_mailhost(context):
    from Products.MailHost.MailHost import MailHost as klass
    update_mailhost(context, klass)


def fix_viewlet_persistence(context):
    # The viewlet storage should be persistent, but some old parts are
    # simple dictionaries, which mean applying the viewlets.xml or
    # editing manage-viewlets only has effect until the next restart.
    from persistent.mapping import PersistentMapping
    from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
    from zope.component import getUtility

    storage = getUtility(IViewletSettingsStorage)
    for setting in (storage._order, storage._hidden):
        for key, value in setting.items():
            if isinstance(value, dict):
                value = PersistentMapping(value)
                setting[key] = value
                logger.info("Made value of key %s a persistent mapping.", key)


def cook_resources(context):
    # When you change a css or javascript, the resources should be
    # cooked again, otherwise on production you will keep seeing old
    # cached resources.
    for registry_id in ('portal_css', 'portal_javascripts'):
        registry = getToolByName(context, registry_id)
        registry.cookResources()


def migrate_to_blob_file_fields(context):
    from plone.app.blob.migrations import migrate
    logger.info("Migrating to blob file fields...")
    migrate(context, 'AnnualReport')
    logger.info("Done migrating to blob file fields.")


def migrate_to_blob_image_fields(context):
    from plone.app.blob.migrations import migrate
    logger.info("Migrating to blob image fields...")
    migrate(context, [
        'Advisory', 'MREvent', 'Pressrelease', 'Study'])
    logger.info("Done migrating to blob image fields.")


def reindex_object_provides_index(context):
    """Reindex the object_provides index.

    This index gives errors when indexing content, for example during
    blob migration:

      ERROR Zope.UnIndex KeywordIndex: unindex_object could not remove
      documentId 1995228665 from index object_provides.  This should not
      happen.

      Traceback (most recent call last):

        File ".../Products/PluginIndexes/common/UnIndex.py", line 160,
              in removeForwardIndexEntry
          indexRow.remove(documentId)
      KeyError: 1995228665

    The errors are ignored and seem harmless, but they clutter the
    log.  We clear the index and reindex it to fix this.
    """
    from Acquisition import aq_get
    catalog = getToolByName(context, 'portal_catalog')
    index_id = 'object_provides'
    logger.info("Reindexing %s index.", index_id)
    catalog.manage_clearIndex([index_id])
    pghandler = ZLogHandler(1000)
    catalog.reindexIndex(index_id, aq_get(context, 'REQUEST', None),
                         pghandler=pghandler)

from PIL import Image, ImageDraw, ImageColor
from random import choice
import cStringIO
from Products.Archetypes.Field import ImageField

def create_lead_image(size=(800, 450), color="blue"):
    """
    Creates an memory object containing an image.
    Expects a size tuple and PIL color.

    :param size: tuple of ints (width, height) default (800, 450)
    :param color: String or PIL color (r,g,b) tuple.
    :return: NamedBlobImage
    """
    # Create an image.
    im = Image.new("RGB", size, color=color)

    # Draw some lines
    draw = ImageDraw.Draw(im)
    color = ImageColor.getrgb(color)
    for i in range(9):
        factor = choice(range(8, 18, 1)) / 10.0
        stroke_color = (
            int(min(color[0] * factor, 255)),
            int(min(color[1] * factor, 255)),
            int(min(color[2] * factor, 255)),
        )
        draw.line(
            [
                (choice(range(0, size[0])), choice(range(0, size[1]))),
                (choice(range(0, size[0])), choice(range(0, size[1])))
            ],
            fill=stroke_color,
            width=int(size[1] / 5)
        )

    # 'Save' the file.
    sio = cStringIO.StringIO()
    im.save(sio, format="PNG")
    sio.seek(0)

    # Create named blob image
    # image_field = ImageField()
    # nbi.data = sio.read()
    # nbi.filename = u"example.png"

    return sio.read()


def move_content(context):
    """
    Search the whole site for content of some theme and type and move it to the
    appropriate folders.

        21 / Strategisch milieubeleid,   "Vergroening economie"
        22 / Instrumenten                "Bestuurskwaliteit"
        -- / ----------,                 "Materialen"
        23 / Milieuhygiëne en klimaat,   "Klimaat"
        24 / Water en zee,               "Hinder"
        25 / Open Ruimte                 "Biodiversiteit"
        26 / Ruimtelijke ordening en mobiliteit, ""
        27 / Participatie en lokale besturen,  "Bestuur"

    :param context:
    :return:
    """
    themes = {
        21: "vergroening-van-de-economie",
        22: "bestuurskwaliteit",
        27: "bestuurskwaliteit",
        23: "klimaat",
        24: "hinder",
        25: "biodiversiteit",
        26: "temp-ruimtelijke-ordening-en-mobiliteit",
    }

    types = [
        ('Advisory', 'advies'),
        ('MREvent', 'evenement'),
        ('Hearing', 'hoorzitting'),
        ('Study', 'studie'),
    ]

    portal = api.portal.get()

    for portal_type, sub_folder in types:
        brains = api.content.find(
            context=portal,
            portal_type=portal_type,
        )
        for brain in brains:
            obj = brain.getObject()

            lockable = ILockable(obj)
            if lockable.locked():
                lockable.unlock()
                logger.info("Unlock %s", obj.title)

            try:
                theme = themes[obj.theme]
            except KeyError:
                theme = 'andere-themas'

            target = portal['themas'][theme][sub_folder]
            api.content.move(source=obj, target=target)
            logger.info("Moved %s to %s %s", obj.title, theme, sub_folder)



def create_theme_folders(context):
    """
    Create theme folders. Subfolders are created by an event subscriber.

    :param context:
    :return: None
    """

    themes = [
        "Vergroening van de economie",
        "Bestuurskwaliteit",
        "Materialen",
        "Klimaat",
        "Hinder",
        "Biodiversiteit",
        "Andere thema's",
        # Temp folders.
        "Temp Ruimtelijke ordening en mobiliteit"
    ]

    portal = getToolByName(context, 'portal_url').getPortalObject()
    folder = portal.get('themas', False)
    if not folder:
        folder = _createObjectByType("Folder", portal, 'themas')
        folder.title = "Thema's"
        transaction.savepoint(optimistic=True)
        workflowTool = getToolByName(folder, "portal_workflow")
        workflowTool.doActionFor(folder, "publish")
        logger.info("%s created", folder)

    for title in themes:
        theme = api.content.create(
            type='Theme',
            title=title,
            container=folder,
            description="%s introductietekst hier." % title,
            secondary=(title == "Overig"),
            image=create_lead_image(size=(600, 600)),
            footerImage=create_lead_image(size=(1200, 600)),
        )
        api.content.transition(obj=theme, transition='publish')
        logger.info("%s created", title)


def to_plone436(context):
    """
    This applies the plone436 profile from minaraad.  This has some
    steps that should only be applied once, during the upgrade to
    Plone 4.3.6
    """

    profile_id = 'profile-Products.minaraad:plone436'
    context.runAllImportStepsFromProfile(profile_id, purge_old=False)

    # Various
    create_theme_folders(context)
    move_content(context)
