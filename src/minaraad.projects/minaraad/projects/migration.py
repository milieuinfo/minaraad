import logging
import re

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName

from minaraad.projects.utils import create_attachment
from minaraad.projects.utils import is_advisory_request

logger = logging.getLogger('minaraad.projects.migration')
# The default profile id of your package:
PROFILE_ID = 'profile-minaraad.projects:default'


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
    context.runImportStepFromProfile(PROFILE_ID, 'action-icons')


def update_types(context):
    context.runImportStepFromProfile(PROFILE_ID, 'typeinfo')


def update_actions(context):
    context.runImportStepFromProfile(PROFILE_ID, 'actions')
    context.runImportStepFromProfile(PROFILE_ID, 'action-icons')


def apply_workflow_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'workflow')
    # Run the update security on the workflow tool.
    logger.info('Updating security settings.  This may take a while...')
    wf_tool = getToolByName(context, 'portal_workflow')
    wf_tool.updateRoleMappings()
    logger.info('Done updating security settings.')


def apply_propertiestool_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'propertiestool')


def migrate_advisories_to_projects(context):
    # This is the second incarnation of this migration.
    # We have already migrated adviezen/2009-2011.
    # Now we want to migrate digibib-1/dossiers-adviezen/2009-2011.
    portal = getToolByName(context, 'portal_url').getPortalObject()
    # advisory_folder = portal['adviezen']
    advisory_folder = portal['digibib-1']['dossiers-adviezen']['2011']
    target = portal['digibib']['projects']
    # We only want to migrate a few specially selected folders.
    hardcoded_id_list = [
        '110519-evaluatie-van-de-werking-2010-van-de-regionale-landschappen'
        '110719-erkenning-van-een-privaat-natuurreservaat-e-409-gondebeek-te-melle-merelbeke-en-oosterzele-oost-vlaanderen',
        '110719-uitbreiding-van-een-erkend-natuurreservaat-e-003-blankaart-te-diksmuide-en-houtlhulst-west-vlaanderen',
        '110823-uitbreiding-van-een-erkend-natuurreservaat-e-111-latemse-meersen-te-sint-martens-latem-oost-vlaanderen',
        '110823-uitbreiding-van-het-erkend-natuurreservaat-e-216-hof-ten-berg-te-galmaarden-vlaams-brabant-en-geraardsbergen-oost-vlaanderen',
        '110824-uitbreiding-erkend-natuurreservaat-e-161-duivenbos-te-herzele',
        '20110930-milieuhandhavingsprogramma-2011',
        'uitbreiding-van-een-erkend-natuurreservaat-e-016-201ctikkebroeken201d-te-kasterlee-en-oud-turnhout-antwerpen',
        ]
    for advisory_id in hardcoded_id_list:
        try:
            advisory = advisory_folder[advisory_id]
        except KeyError:
            logger.warn("Advisory id %s not found.", advisory_id)
            continue
        logger.info("Migrating %s", advisory_id)

        # Determine fields for the Project.
        title_parts = advisory.Title().split(' ')
        date_part = title_parts[0]
        title_part = ' '.join(title_parts[1:]).strip('-').strip()
        try:
            day = int(date_part[-2:])
            month = int(date_part[-4:-2])
            year = 2011
            advisory_date = DateTime(year, month, day)
        except:
            # the field is mandatory
            advisory_date = DateTime()

        # Create a Project.
        project_id = target.generateUniqueId('Project')
        target.invokeFactory('Project', id=project_id)
        project = target[project_id]

        # First we must set the date and we cannot do that in the
        # later processForm call.
        project.setAdvisory_date(advisory_date)
        fields = dict(
            title=title_part,
            )
        # Process the form:
        project.processForm(values=fields)
        # processForm may have caused a rename
        project_id = project.getId()
        # The project_id will actually not be nice because it
        # depends on the internal project id field and we
        # cannot determine that; so we should enable an
        # automatic rename when the object gets edited:
        project.markCreationFlag()
        logger.info("Created a project with id %s.", project_id)

        for doc in advisory.contentValues():
            if (is_advisory_request(doc) and
                project.getAdvisory_request().getSize() == 0):
                project.setAdvisory_request(doc.getFile())
                logger.info("Saved advisory request.")
            else:
                create_attachment(project, doc, published=False)
    logger.info("Done migrating/copying advisories to projects.")


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

    logger.info("Ran '_update_agenda_item_attachment_counter' on %s meetings." % len(brains))

def rename_attachments(context):
    """ Rename attachments in meetings that are called 'Billage XX'
    as this is now automatically generated.
    """
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type='Meeting')
    att_count = 0
    exp = re.compile(r'^Billage *(\d+) *:? *(.*)')
    
    for brain in brains:
        meeting = brain.getObject()
        attachments = catalog.searchResults(
            portal_type = 'FileAttachment',
            path = '/'.join(meeting.getPhysicalPath()))

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
            logger.info('Unable to wake brain at %s' % brain.getURL())

        if project.getAdvisory_type() in ['abstention', 'reject_points']:
            project.setAdvisory_type('abstention_rejection')
            p_count += 1

    logger.info('Updated advisory type for %s projects' % p_count)
