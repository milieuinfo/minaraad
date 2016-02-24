# -*- coding: utf-8 -*-

from Acquisition import aq_parent
from collective.embedly.interfaces import IEmbedlySettings
from collective.mailchimp.interfaces import IMailchimpSettings
from persistent.list import PersistentList
from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageChops
from plone import api
from plone.i18n.normalizer import idnormalizer
from plone.locking.interfaces import ILockable
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.registry.interfaces import IRegistry
from Products.Archetypes.utils import mapply
from Products.Archetypes.utils import shasattr
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.contentmigration.archetypes import InplaceATFolderMigrator
from Products.contentmigration.basemigrator.walker import CatalogWalker
from Products.minaraad.attendees import Attendee
from Products.minaraad.content.interfaces import IUseContact
from Products.minaraad.events import save_theme_name
from Products.minaraad.interfaces import IAttendeeManager
from Products.SimpleAttachment.setuphandlers import registerImagesFormControllerActions  # noqa
from Products.ZCatalog.ProgressHandler import ZLogHandler
from random import choice
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.component import getUtility
from zope.component import queryUtility
from zope.container import contained

import cStringIO
import logging
import transaction


logger = logging.getLogger('Products.minaraad.migrations')
# The default profile id of your package:
PROFILE_ID = 'profile-Products.minaraad:default'
# Mapping from old theme integer to new Theme object id.
OLD_THEMES = {
    21: "vergroening-van-de-economie",
    22: "bestuurskwaliteit",
    27: "bestuurskwaliteit",
    23: "klimaat",
    24: "hinder",
    25: "biodiversiteit",
    26: "temp-ruimtelijke-ordening-en-mobiliteit",
}
CONTACT_TEXT = """
<p class="lead">Strategische adviesraad Minaraad Kliniekstraat 25<br />
B-1070 Brussel (Anderlecht)<br />
Tel. 02 558 01 30<br />
E-mail: <a href="mailto:info@minaraad.be">info@minaraad.be</a></p>
<p>Het secretariaat en de vergaderzalen bevinden zich op de 4de verdieping.</p>
<h2>Routebeschrijving</h2>
<p>De Minaraad ligt op wandelafstand van het NMBS-station Brussel-Zuid
(800m) en vlakbij het metrostation Clemenceau (200m).</p>
<p>Vanaf NMBS-station Brussel-Zuid (te voet 10 min.):</p>
<ul>
  <li>uitgang Zuidertoren nemen;</li>
  <li>Paul-Henri Spaaklaan volgen tot Baraplein;</li>
  <li>Baraplein oversteken en Clemenceaustraat ingaan;</li>
  <li>2de straat rechts is de Kliniekstraat.</li>
</ul>
<p>Vanaf NMBS-station Brussel-Zuid (metro 5 min.):</p>
<ul>
  <li>metrolijn 2 of 6 nemen;</li>
  <li>afstappen halte Clemenceau;</li>
  <li>uitgang Kliniekstraat nemen;</li>
  <li>linksaf de Kliniekstraat inwandelen;</li>
  <li>Clemenceaustraat en Bissestraat dwarsen.</li>
</ul>
"""

# API keys
EMBEDLY_API_KEY = "6516fa92558c4e57a29e71622263bfc5"
MAILCHIMP_API_KEY = "3da524051a2e46d5408de7c53d61e1e3-us12"


def set_link_integrity_checking(context, value):
    ptool = getToolByName(context, 'portal_properties')
    props = getattr(ptool, 'site_properties', None)
    if props is not None:
        props._updateProperty('enable_link_integrity_checks', value)


def enable_link_integrity_checking(context):
    # This is the default on the live site.
    set_link_integrity_checking(context, True)
    logger.info('Enabled link integrity checking.')


def disable_link_integrity_checking(context):
    # During migrations, link integrity checking is just in the way, especially
    # when you are migrating content in place: the content will be gone for a
    # millisecond and then return, so you don't want link interity checking to
    # come in and spoil the party.
    set_link_integrity_checking(context, False)
    logger.info('Disabled link integrity checking.')


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

    return sio.read()


def unassign_portlets(context):
    """
    Remove assignements of the portlets in the right column.

    :param context:
    :return:
    """
    portal = api.portal.get()
    contained.fixing_up = True
    manager = getUtility(
        IPortletManager, name=u'plone.rightcolumn', context=portal)
    assignments = getMultiAdapter((portal, manager), IPortletAssignmentMapping)
    for portlet in assignments:
        del assignments[portlet]
    contained.fixing_up = False


def themas_select_default_page_and_view(context):
    """
    Add default page and select view for themas.
    :param contect:
    :return: None
    """

    page_uid = "thema-lijst"
    folder = api.portal.get().themas
    page = api.content.create(
        type='Document',
        title="Thema's",
        id=page_uid,
        container=folder,
    )
    api.content.transition(obj=page, transition='publish')
    folder.moveObjectsToTop(page_uid)
    folder.setDefaultPage(page_uid)
    page.setLayout("themes")
    logger.info("Created, made default page and set layout for %s", folder)


def homepage_select_default_page_and_view(context):
    """
    Add default page and select view for homepage.
    :param contect:
    :return: None
    """
    portal = api.portal.get()

    homepage = api.content.create(
        type='Document',
        title="Milieu- en Natuurraad van Vlaanderen (Minaraad)",
        id="homepage",
        container=portal,
        description=("De Minaraad is de strategische adviesraad voor het "
                     "beleidsdomein Leefmilieu, Natuur en Energie van de "
                     "Vlaamse Overheid."),
    )
    api.content.transition(obj=homepage, transition='publish')
    portal.setDefaultPage("homepage")
    homepage.setLayout("homepage")
    logger.info("Created, made default page and set layout for %s", homepage)


def setup_various(context):
    """
    Setup about page:

        - Create zoeken folder
        - Move `Jaarverslagen` into `Algemeen`
        - Move `Contact` to portal root
        - Set contact page view to contact_view
        - Rename "Gebouw SAR Minaraad.jpg" to "gebouw-sar-minaraad.jpg"
        - Rename `algemeen` > `Over de Minaraad`
        - Sort items.

    :param context:
    :return: None
    """

    portal = api.portal.get()

    # Create zoeken folder
    zoeken = portal.get('zoeken')
    if not zoeken:
        zoeken = api.content.create(
            type='Folder',
            title="Zoeken",
            container=portal,
        )
        api.content.transition(obj=zoeken, transition='publish')
        logger.info("%s created", zoeken)

    # Move `Jaarverslagen` into `Algemeen`
    report = portal.get('jaarverslag')
    about = portal.get('Algemeen')
    if report and about:
        api.content.move(source=report, target=about)
        logger.info("Moved `jaarverslag` into `Algemeen`")

    # Move `Contact` to portal root
    if about:
        contact = about.get('Contact')
        if contact:
            api.content.move(source=contact, target=portal)
            logger.info("Moved `Contact` into portal root")

        # Rename `algemeen` > `Over de Minaraad`
        about.title = 'Over de Minaraad'
        api.content.rename(obj=about, new_id="over-de-minaraad")
        logger.info("Renamed Algemeen > Over de Minaraad")

    # set contact view on contact
    contact_folder = portal.get('Contact')
    plattegrond = contact_folder.get('plattegrond')

    contact_folder_default = contact_folder.getProperty('default_page', None)
    if contact_folder_default:
        contact_folder._updateProperty('default_page', 'plattegrond')
    else:
        contact_folder._setProperty('default_page', 'plattegrond')
    contact_layout = plattegrond.getProperty('layout', None)
    if contact_layout:
        plattegrond._updateProperty('layout', 'contact_view')
    else:
        plattegrond._setProperty('layout', 'contact_view')
    plattegrond.setText(CONTACT_TEXT)

    # rename image
    image_orig = portal.get('Contact').get('Gebouw SAR Minaraad.JPG')
    image_dest = portal.get('Contact').get('gebouw-sar-minaraad.jpg')
    if image_orig and not image_dest:
        api.content.rename(obj=image_orig, new_id='gebouw-sar-minaraad.jpg')

    # Sort items.
    items = [
        'themas',
        'over-de-minaraad',
        'digibib',
        'Contact',
        'zoeken',
    ]
    items.reverse()
    for uid in items:
        portal.moveObjectsToTop(uid)
        logger.info('%s is now on top.', uid)


def move_redundant_folders(context):
    """
    Backup redundant folders into a private 'Dropped items' folder.

    :param context:
    :return: None
    """
    portal = api.portal.get()
    folder = portal.get('vervallen-items')
    if not folder:
        folder = api.content.create(
            type='Folder',
            title='Vervallen items',
            container=portal,
            description=("Tijdens de migratie is onderliggende inhoud "
                         "waarschijnlijk overbodig geworden."),
        )

    redundant_items = [
        'adviezen',
        'studies',
        'hoorzittingen',
        'evenementen',
        'nieuwsbrieven',
    ]

    for uid in redundant_items:
        obj = portal.get(uid)
        if obj:
            api.content.move(source=obj, target=folder)
            logger.info("Moved %s to Vervallen items.", uid)


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

    types = [
        'Advisory',
        'MREvent',
        'Hearing',
        'Study',
    ]

    portal = api.portal.get()
    brains = api.content.find(
        context=portal,
        portal_type=types,
    )
    for brain in brains:
        obj = brain.getObject()

        lockable = ILockable(obj)
        if lockable.locked():
            lockable.unlock()
            logger.info("Unlock %s", obj.title)

        try:
            theme = OLD_THEMES[obj.theme]
        except KeyError:
            theme = 'andere-themas'

        target = portal['themas'][theme]
        if aq_parent(obj).getPhysicalPath() == target.getPhysicalPath():
            continue

        api.content.move(source=obj, target=target)
        logger.info("Moved %s to %s", obj.title, theme)


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
    folder = portal.get('themas')
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


def migrate_project_themes(context):
    """Migrate project themes.

    Migrate projects from old-style theme integers to new-style Theme objects.

    In move_content we moved Studies, etc, to the Theme object folders
    based on their theme integers.

    Now we edit Projects.  They also had their theme stored as integer
    in the theme field, from the OldThemeMixin.

    Now we link them to the appropriate theme folders.  The theme_path
    field will contain the path to the theme.  That is also what we get
    from the minaraad.theme_path vocabulary.

    And just like before, we use getThemeName and setThemeName in
    events.save_theme_name to save the theme name.
    """
    portal = api.portal.get()
    portal_path = '/'.join(portal.getPhysicalPath())
    print 'portal_path', portal_path
    brains = api.content.find(
        context=portal,
        portal_type='Project',
    )
    for brain in brains:
        obj = brain.getObject()
        old_theme_name = obj.getThemeName()
        # Note: theme might be None, but that is fine.

        old_theme_id = getattr(obj, 'theme', None)
        lockable = ILockable(obj)
        if lockable.locked():
            lockable.unlock()
            logger.info("Unlock %s", obj.title)

        try:
            theme = OLD_THEMES[old_theme_id]
        except KeyError:
            theme = 'andere-themas'

        theme_path = '/'.join([portal_path, 'themas', theme])
        obj.setTheme_path(theme_path)
        save_theme_name(obj)
        logger.info("Moved Project %s theme from %r (%r) to %r",
                    brain.getPath(), old_theme_name, old_theme_id,
                    obj.getThemeName())


def apply_extra_product_profiles(context):
    """
    This applies the plone436 profile from minaraad.  This has some
    steps that should only be applied once, during the upgrade to
    Plone 4.3.6
    """

    profiles = [
        "profile-eea.facetednavigation:default",
        "profile-collective.mailchimp:default",
        "profile-collective.embedly:default",
        "profile-plone.app.imagecropping:default",
        "profile-minaraad.theme:default"]

    for profile_id in profiles:
        context.runAllImportStepsFromProfile(profile_id, purge_old=False)


def to_plone436(context):
    """
    This applies the plone436 profile from minaraad.  This has some
    steps that should only be applied once, during the upgrade to
    Plone 4.3.6
    """

    profile_id = 'profile-Products.minaraad:plone436'
    context.runAllImportStepsFromProfile(profile_id, purge_old=False)


def activate_theme(context):
    """Activate diazo theme."""
    from plone.app.theming.utils import getTheme
    from plone.app.theming.utils import applyTheme
    theme = getTheme('minaraad')
    applyTheme(theme)
    logger.info('Activated minaraad diazo theme.')


def setup_faceted_navigation(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    docs = portal['zoeken']
    subtyper = docs.restrictedTraverse('@@faceted_subtyper')
    subtyper.enable()
    importer = docs.restrictedTraverse('@@faceted_exportimport')
    criteria_file = open('faceted_criteria.xml')
    importer.import_xml(import_file=criteria_file)
    logger.info("Configured faceted navigation for /zoeken")


def rebuild_date_indexes(context):
    catalog = getToolByName(context, 'portal_catalog')
    idxs = ['effectiveRange', 'Date', 'getStart_time', 'getDate',
            'expires', 'created', 'modified', 'published',
            'get_end_time', 'effective', 'start']
    catalog.manage_clearIndex(ids=idxs)
    catalog.manage_reindexIndex(ids=idxs)


def unininstall_classic_theme(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    installer = getToolByName(context, 'portal_quickinstaller')
    if getattr(portal, 'persberichten', None):
        portal.manage_delObjects(ids=['persberichten'])
    for product in installer.listInstalledProducts():
        if product['id'] == 'plonetheme.classic':
            installer.uninstallProducts(products=['plonetheme.classic'])
            logger.info("Plone Classic Theme uninstalled")


def migrate_foto_field_to_imageattachment(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    migrate_types = ['Advisory', 'MREvent', 'Hearing', 'Study']
    for ctype in migrate_types:
        registerImagesFormControllerActions(portal, contentType=ctype,
                                            template='base_edit')

    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog({'portal_type': migrate_types})
    for brain in brains:
        obj = brain.getObject()
        foto = obj.getFoto()
        if foto is None:
            continue
        filename = foto.filename
        if filename and filename != '':
            # create ImageAttachment
            new_context = context.portal_factory.doCreate(obj, obj.getId())
            newImageId = new_context.invokeFactory(
                id=idnormalizer.normalize(filename),
                type_name='ImageAttachment')
            new_obj = getattr(new_context, newImageId)
            new_obj.setTitle(filename)
            new_obj.setImage(foto.data)
            new_obj.reindexObject()
            # remove image from foto field
            obj.setFoto(None)
            logger.info("Migrated foto field of %s to ImageAttachment",
                        brain.getPath())


def initialize_rich_text_fields_object(instance):
    """New rich text fields should have mimetype text/html.

    New richtext fields, get treated as text/plain.  This means you do
    not get a rich text editor.  Saving it once in the Plone UI helps.
    Let's do that here.

    Adapted from setDefaults in Archetypes BasicSchema.

    Taken over from knmp.im.
    """
    # default_output_type = 'text/x-html-safe'
    default_output_type = 'text/html'
    mimetype = 'text/html'
    schema = instance.Schema()
    fixed = False
    for field in schema.values():
        # We only need to do this for fields with one specific mimetype.
        if not shasattr(field, 'default_output_type'):
            continue
        if field.default_output_type != default_output_type:
            continue
        # only touch writable fields
        mutator = field.getMutator(instance)
        if mutator is None:
            continue
        base_unit = field.getBaseUnit(instance)
        # This check was in knmp.im, but somehow fails for us here: the new
        # popular_summary field has the correct mimetype already, but it still
        # shows up as plain textarea widget.
        # if base_unit.mimetype == mimetype:
        #     continue
        # If content has already been set, we respect it.
        if base_unit:
            continue
        default = field.getDefault(instance)
        args = (default,)
        kw = {'field': field.__name__,
              '_initializing_': True}
        kw['mimetype'] = mimetype
        mapply(mutator, *args, **kw)
        fixed = True
    return fixed


def initialize_rich_text_fields_all_advisories(context):
    """Initialize new rich text fields for all Advisories.
    """
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog({'portal_type': 'Advisory'})
    fixed = 0
    for brain in brains:
        obj = brain.getObject()
        if initialize_rich_text_fields_object(obj):
            fixed += 1
    logger.info('Initialized fields in %d out of %d Advisories.',
                fixed, len(brains))


def initialize_rich_text_fields_all_themes(context):
    """Initialize new rich text fields for all Advisories.
    """
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog({'portal_type': 'Theme'})
    fixed = 0
    for brain in brains:
        obj = brain.getObject()
        if initialize_rich_text_fields_object(obj):
            fixed += 1
    logger.info('Initialized fields in %d out of %d Themes.',
                fixed, len(brains))


def remove_broken_cachefu(context):
    """Cleanup old CacheFu.

    This is a part of what is done in plone.app.upgrade/v40/alphas.py in
    function removeBrokenCacheFu.  For some reason it was still needed.
    I guess we manually uninstalled CacheFu in Plone 3 but this left a
    utility behind.  And because the portal tools were gone, the
    p.a.upgrade step was not fully executed.
    """
    from Products.CMFCore.interfaces import ICachingPolicyManager
    # portal = api.portal.get()
    # sm = getSiteManager(context=portal)
    sm = getSiteManager()
    for util in sm.getAllUtilitiesRegisteredFor(ICachingPolicyManager):
        if util.id == 'broken':
            # The official way does not work...
            # sm.unregisterUtility(
            #    component=util, provided=ICachingPolicyManager)
            try:
                del sm.utilities._subscribers[0][ICachingPolicyManager]
            except (IndexError, KeyError):
                # This happens when you run the upgrade step a second time.
                # But after
                logger.warn('Failed to unregister Caching Policy Manager.')
            else:
                # _subscribers is a standard non peristent list, so mark its
                # parent as changed.
                sm.utilities._p_changed = True
                logger.info('Unregistered the CacheFu Caching Policy Manager.')
            break
    else:
        logger.info('Caching Policy Manager was already unregistered.')


def update_catalog_metadata(context):
    """Update catalog metadata.

    In this case we want to update the getIcon column because it
    references no longer available .gif files.
    """
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type=[
        'NewsItem',
        'AnnualReport',
        'ContactPerson',
        'FileAttachment',
        'File',
        ])
    for brain in brains:
        obj = brain.getObject()
        path = brain.getPath()
        # Passing in a valid but inexpensive index, makes sure we
        # don't reindex expensive indexes like SearchableText.
        catalog.catalog_object(obj, path, ['id'], update_metadata=True)
    logger.info('Updated catalog metadata for %d items.', len(brains))


def update_attendees_to_anonymous(context):
    """Update _attendees object to store unauthenticated info.

    See MINA-103.  We no longer require people to login.  So we no
    longer store just the member id, but an Attendee object.
    """
    catalog = getToolByName(context, 'portal_catalog')
    member_tool = getToolByName(context, 'portal_membership')
    brains = catalog.unrestrictedSearchResults(
        portal_type=[
            'Hearing',
            'MREvent',
            ])

    obj_count = 0
    non_members = []
    non_attendees = []
    for brain in brains:
        try:
            obj = brain.getObject()
        except (AttributeError, ValueError):
            logger.warning('Could not wake object at: %s' % brain.getURL())
            continue

        adapter = IAttendeeManager(obj)
        attendees = adapter.attendees()
        if not attendees:
            continue
        if isinstance(attendees[0], Attendee):
            # Already the new storage format.
            continue
        new_attendees = PersistentList()
        for memberid in attendees:
            member = member_tool.getMemberById(memberid)
            if member is None:
                non_members.append(memberid)
                continue
            attendee = adapter.get_from_member(member)
            if attendee is None:
                non_attendees.append(member.getId())
                continue
            new_attendees.append(attendee)

        obj._attendees = new_attendees
        obj_count += 1

    logger.info('Updated %s objects to unauthenticated attendees. '
                'Found %s non members. '
                'Found %s members who could not be turned into attendees. ',
                obj_count, len(non_members), len(non_attendees))
    if non_members:
        logger.info('Non members:')
        for memberid in non_members:
            logger.info(memberid)
    if non_attendees:
        logger.info('Non attendees:')
        for memberid in non_attendees:
            logger.info(memberid)


def remove_lots_of_users(context):
    """Remove lots of users.

    We only keep Managers and Editors, etcetera, and users with access
    to the Digibib.

    So basically: users that only have the Member role, can be removed.

    Code is adapted from plone.app.controlpanel usergroups.py, method
    deleteMembers.
    """
    portal = getToolByName(context, 'portal_url').getPortalObject()
    digibib = portal.digibib
    mtool = getToolByName(context, 'portal_membership')
    member_ids = mtool.listMemberIds()
    to_remove = []
    to_keep = []
    for member_id in member_ids:
        member = mtool.getMemberById(member_id)
        if member is None:
            logger.warn('Member with id %r does not exist.', member_id)
            continue
        # Members can get roles from groups, but that is covered in the
        # getRolesInContext call.  Well, let's be safe.
        # We expect these groups: ['AuthenticatedUsers']
        groups = member.getGroups()
        # We expect these global roles: ['Member', 'Authenticated']
        global_roles = member.getRoles()
        # We expect these roles in the context of the digibib:
        # ['Member', 'Authenticated']
        digibib_roles = member.getRolesInContext(digibib)
        # Remove uninteresting roles and groups:
        for group in ('AuthenticatedUsers', ):
            if group in groups:
                groups.remove(group)
        for role in ('Member', 'Authenticated'):
            if role in global_roles:
                global_roles.remove(role)
            if role in digibib_roles:
                digibib_roles.remove(role)
        if digibib_roles or global_roles or groups:
            to_keep.append(member_id)
        else:
            to_remove.append(member_id)

    logger.info('To remove: %d', len(to_remove))
    logger.info('To keep: %d', len(to_keep))

    # Delete members in acl_users.
    acl_users = getToolByName(context, 'acl_users')
    acl_users.userFolderDelUsers(to_remove)
    logger.info('Deleted users from acl_users.')

    # Delete member data in portal_memberdata.
    mdtool = getToolByName(context, 'portal_memberdata', None)
    if mdtool is not None:
        for member_id in to_remove:
            mdtool.deleteMemberData(member_id)
    logger.info('Deleted users from portal_memberdata.')

    # Delete members' local roles.
    # Note that we have a patch in place in patches.py,
    # which makes this not load the entire site.
    logger.info('About to delete local roles. This can take a while...')
    mtool.deleteLocalRoles(portal, to_remove, reindex=1, recursive=1)
    logger.info('Done.')


def setup_api_keys(context):
    """ setup api keys

    Add mailchimp and embedly api_key settings.
    Specify the keys EMBEDLY_API_KEY and MAILCHIMP_API_KEY at the top of this
    document.
    """
    registry = getUtility(IRegistry)

    if EMBEDLY_API_KEY:
        embedly_settings = registry.forInterface(IEmbedlySettings, False)
        if embedly_settings:
            embedly_settings.api_key = unicode(EMBEDLY_API_KEY)
            logger.info("Set the embedly api-key")
    else:
        raise ValueError(
            'Missing EMBEDLY_API_KEY in Products/minaraad/migration.py.')

    if MAILCHIMP_API_KEY:
        mailchimp_settings = registry.forInterface(IMailchimpSettings, False)
        if mailchimp_settings:
            mailchimp_settings.api_key = unicode(MAILCHIMP_API_KEY)
            logger.info("Set te mailchimp api-key")
    else:
        raise ValueError(
            'Missing MAILCHIMP_API_KEY in Products/minaraad/migration.py.')


def migrate_hearings_to_events(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    catalog = getToolByName(portal, 'portal_catalog')
    hearings = catalog.unrestrictedSearchResults(portal_type='Hearing')
    if len(hearings) == 0:
        logger.info('No hearings found, so no migration needed.')
        return
    events = catalog.unrestrictedSearchResults(portal_type='MREvent')
    logger.info('Found %d hearings and %d events.', len(hearings), len(events))
    logger.info('Migrating Hearing to MREvent. This can take a while...')

    class HearingMigrator(InplaceATFolderMigrator):
        src_portal_type = 'Hearing'
        src_meta_type = 'Hearing'
        dst_portal_type = 'MREvent'
        dst_meta_type = 'MREvent'

    walker = CatalogWalker(portal, HearingMigrator)
    walker()
    logger.info('Done migrating Hearing to MREvent.')
    events = catalog.unrestrictedSearchResults(portal_type='MREvent')
    hearings = catalog.unrestrictedSearchResults(portal_type='Hearing')
    logger.info('Found %d hearings and %d events.', len(hearings), len(events))


def update_reference_catalog(context):
    # Migrated Hearings have duplicate coordinators and authors.  Best way to
    # fix this is by updating the reference catalog.  This loses several dozen
    # references more than I expect, but those were probably pointing to no
    # longer existing content.
    from Products.Archetypes.config import REFERENCE_CATALOG
    from Products.ZCatalog.ProgressHandler import ZLogHandler
    tool = getToolByName(context, REFERENCE_CATALOG)
    handler = ZLogHandler(100)
    tool.refreshCatalog(clear=1, pghandler=handler)


def trim_image_whitespace(context):
    """ trim_image_whitespace
    the the whitespace of images.
    """

    def whitespace_trim(im, color_cutoff=20, max_border_width=10):
        """ whitespace_trim
        trim the white border from an image
        color_cutoff parameter specifies how far off-white the border
        can be.
        if no white border is detected this function returns zero
        """

        # check if border is white(ish)
        border_color = im.getpixel((0, 0))
        if type(border_color) == int:
            border_color = [border_color]
        for color in border_color:
            if color < 255 - color_cutoff:
                return

        # create blank image for comparing
        def bbox_size(bbox):
            if not bbox:
                return
            ret_value = (bbox[2]-bbox[0]) * (bbox[3]-bbox[1])
            return ret_value
        bbox = []
        for corner in [(0,0), (im.size[0] - 1, im.size[1] - 1)]:
            bg = Image.new(im.mode, im.size, im.getpixel(corner))
            diff = ImageChops.difference(im, bg)
            diff = ImageChops.add(diff, diff, 2.0, -40)
            potential_bbox = diff.getbbox()
            if bbox_size(potential_bbox) < bbox_size(bbox) or not bbox:
                bbox = potential_bbox
        if not bbox:
            return

        # get the width of the border
        border_width = max(bbox[0], bbox[1],
                bbox[2] - im.size[0], bbox[3] - im.size[1])

        if bbox[:2] == (0,0) and bbox[2:] == im.size:
            return

        # return cropped image if border is smaller than max_border_width
        if border_width <= max_border_width:
            return im.crop(bbox)

    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog.searchResults(portal_type=['Image', 'ImageAttachment'])

    for image in brains:
        img = cStringIO.StringIO(str(image.getObject().getImage().data))
        img = Image.open(img)
        img_orig = img
        if not img:
            continue
        trimmed = False
        for depth in range(3):
            tmp = whitespace_trim(img)
            if not tmp:
                break
            trimmed = True
            img = tmp
        if trimmed:
            logger.info("trimming %s" % image.getObject().Title())
            output = cStringIO.StringIO()
            img.save(output, img_orig.format)
            image.getObject().setImage(output.getvalue())
            output.close()
        img.close()


def upgrade_simple_attachment(context):
    installer = getToolByName(context, 'portal_quickinstaller')
    installer.upgradeProduct('Products.SimpleAttachment')
    logger.info("Upgraded Products.SimpleAttachment.")
