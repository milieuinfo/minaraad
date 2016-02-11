import logging
import re

from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.ProgressHandler import ZLogHandler
from ZODB.POSException import ConflictError
from persistent.dict import PersistentDict

logger = logging.getLogger('minaraad.projects.migration')
# The default profile id of your package:
PROFILE_ID = 'profile-minaraad.projects:default'
# Profile with a few special fixes:
FIXES_PROFILE_ID = 'profile-minaraad.projects:fixes'


def extend_minaraad_properties(context):
    """ Adds "secretary_email" and "Daily governance board" group
    properties in minaraad properties.
    """
    portal_props = getToolByName(context, 'portal_properties')
    props = portal_props.minaraad_properties

    new_props = [{'name': 'secretary_email',
                  'type': 'string',
                  'default': 'to_be_changed@example.com'},
                 {'name': 'governance_board',
                  'type': 'string',
                  'default': ''}]

    for prop in new_props:
        if not props.hasProperty(prop['name']):
            props._setProperty(prop['name'], prop['default'], prop['type'])
            logger.info('Added property %r with default value %r',
                        prop['name'], prop['default'])


def update_controlpanel(context):
    context.runImportStepFromProfile(PROFILE_ID, 'controlpanel')


def update_types(context):
    context.runImportStepFromProfile(PROFILE_ID, 'typeinfo')


def update_actions(context):
    context.runImportStepFromProfile(PROFILE_ID, 'actions')


def apply_workflow_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'workflow')
    # Run the update security on the workflow tool.
    logger.info('Updating security settings.  This may take a while...')
    wf_tool = getToolByName(context, 'portal_workflow')
    wf_tool.updateRoleMappings()
    logger.info('Done updating security settings.')


def apply_propertiestool_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'propertiestool')


def fix_double_invitees(context):
    """Some people are twice in the invitees of a meeting.  Fix that.

    Especially, /minaraad/digibib/meetings/20111018 has invited both
    Bert.wierbos@telenet.be and bert.wierbos@telenet.be.  The first
    one should be removed, and this double user account should also be
    removed, but we will do that part manually.
    """
    portal_url = getToolByName(context, 'portal_url')()
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type='Meeting')
    for brain in brains:
        meeting = brain.getObject()
        invited = meeting.get_invited_people()
        lower_keys = [key.lower() for key in invited.keys()]
        if len(lower_keys) == len(set(lower_keys)):
            # No problem here.
            continue
        logger.info("Double invitees for %s", meeting.absolute_url())
        for user_id in set(invited.keys()).difference(set(lower_keys)):
            logger.info("Checking invitee %s", user_id)
            # This check missed double items like user ids Joe and
            # JOE, but that should be fine; reported in the log above
            # though.
            if user_id.lower() in invited.keys():
                # So both user_id and USER_ID or User_Id or something
                # like that have been invited.
                logger.info("Removing double user id %s from invitees of %s",
                            user_id, meeting.absolute_url())
                logger.warn("You may want to remove "
                            "%s/prefs_user_details?userid=%s", portal_url,
                            user_id)
                del invited[user_id]


def update_attachment_counts(context):
    """ Run the '_update_agenda_item_attachment_counter' on each meeting
    to compute the number of attachments.
    """
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type='Meeting')
    for brain in brains:
        meeting = brain.getObject()
        meeting._update_agenda_item_attachment_counter()

    logger.info("Ran '_update_agenda_item_attachment_counter' on %s meetings."
                % len(brains))


def rename_attachments(context):
    """ Rename attachments in meetings that are called 'Bijlage XX'
    as this is now automatically generated.
    """
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type='Meeting')
    att_count = 0
    exp = re.compile(r'^[Bb]ijlage *(\d+) *:? *(.*)')

    for brain in brains:
        meeting = brain.getObject()
        attachments = catalog.searchResults(
            portal_type='FileAttachment',
            path='/'.join(meeting.getPhysicalPath()))

        for att in attachments:
            match = exp.match(att.Title)
            if match is None:
                continue

            attachment = att.getObject()
            attachment.title = match.groups()[-1]
            attachment.reindexObject()
            att_count += 1

    logger.info("Updated %s attachment title in %s meetings" % (
        att_count, len(brains)))


def update_project_advisory_type(context):
    """ The 'absention' and 'reject_points' keys have been removed
    from the advisory type vocabulary and merged into
    'abstention_rejection'.
    We update existing projects to use the new vocabulary.
    """
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type='Project')
    p_count = 0

    for brain in brains:
        try:
            project = brain.getObject()
        except:
            logger.warn('Unable to wake brain at %s' % brain.getURL())
            continue

        if project.getAdvisory_type() in ['abstention', 'reject_points']:
            project.setAdvisory_type('abstention_rejection')
            p_count += 1

    logger.info('Updated advisory type for %s projects' % p_count)


def reindex_digibib_containers(context):
    portal_url = getToolByName(context, 'portal_url')
    portal = portal_url.getPortalObject()
    digibib = getattr(portal, 'digibib')
    if not digibib:
        logger.warn("No digibib")
        return
    for obj in digibib.contentValues():
        obj.reindexObject()


def use_location_uid_in_cached_locations(context):
    """ We save the UID of the Organisation object in the saved
    location annotation of the meeting o we only update those
    when the location object is saved.
    """
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type='Meeting')
    m_up_count = 0
    m_cl_count = 0

    for brain in brains:
        try:
            meeting = brain.getObject()
        except:
            logger.warn('Unable to wake brain at %s' % brain.getURL())
            continue

        location = meeting.getMeetinglocation()
        annotations = meeting.get_saved_location()

        if not location:
            if not annotations:
                # Well, nothing to do here.
                continue

            annotations = PersistentDict()
            m_cl_count += 1
            continue

        if 'UID' in annotations:
            # Already updated
            continue

        annotations['UID'] = location.UID()
        m_up_count += 1

    logger.info('%s meetings updated' % m_up_count)
    logger.info('%s meetings cleaned' % m_cl_count)


def apply_skin_profile(context):
    context.runImportStepFromProfile(PROFILE_ID, 'skins')


def apply_factory_profile(context):
    context.runImportStepFromProfile(PROFILE_ID, 'factorytool')


def apply_types_fixes(context):
    context.runImportStepFromProfile(FIXES_PROFILE_ID, 'typeinfo')


def run_catalog_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'catalog')


def update_catalog_metadata(context, types=None):
    """Update catalog metadata.

    Adapted from updateIconMetadata in plone.app.upgrade v40/betas.py.
    """
    catalog = getToolByName(context, 'portal_catalog')
    search = catalog.unrestrictedSearchResults
    if types is None:
        logger.info('Updating catalog metadata.')
        brains = search(sort_on="path")
    else:
        if isinstance(types, basestring):
            types = [types]
        logger.info('Updating catalog metadata for %s.', ', '.join(types))
        brains = search(portal_type=types, sort_on="path")
    num_objects = len(brains)
    # Yes, this logs quite often, but I just know I am going to thank
    # myself for that...  Feedback about progress is good for my heart.
    # [Maurits]
    pghandler = ZLogHandler(10)
    pghandler.init('Updating catalog metadata', num_objects)
    i = 0
    for brain in brains:
        pghandler.report(i)
        obj = brain.getObject()
        # passing in a valid but inexpensive index, makes sure we don't
        # reindex the entire catalog including expensive indexes like
        # SearchableText
        brain_path = brain.getPath()
        try:
            catalog.catalog_object(obj, brain_path, ['id'], True, pghandler)
        except ConflictError:
            raise
        except Exception:
            pass
        i += 1
    pghandler.finish()
    logger.info('Done updating catalog metadata.')


def update_meeting_project_metadata(context):
    update_catalog_metadata(context, types=['Meeting', 'Project'])


def update_rolemap(context):
    context.runImportStepFromProfile(PROFILE_ID, 'rolemap')


def migrate_to_blob_fields(context):
    from plone.app.blob.migrations import migrate
    logger.info("Migrating to blob fields...")
    migrate(context, 'Project')
    logger.info("Done migrating to blob fields.")


def agenda_item_project_set_summary_html(context):
    """Set the mimetype of the summary to text/html.

    Otherwise when editing you get a bare textarea and cannot save it.
    """
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type='AgendaItemProject')
    num_objects = len(brains)
    logger.info("Updating agenda item summaries.")
    fixed = 0
    pghandler = ZLogHandler(100)
    pghandler.init('Setting mimetype html for agenda item summaries',
                   num_objects)
    for index, brain in enumerate(brains):
        pghandler.report(index)
        obj = brain.getObject()
        if obj.summary.mimetype != 'text/html':
            obj.summary.mimetype = 'text/html'
            fixed += 1
    pghandler.finish()
    logger.info("Have set summary mimetype to text/html for {0}/{1} agenda "
                "items.".format(fixed, len(brains)))
