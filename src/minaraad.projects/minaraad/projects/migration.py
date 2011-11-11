import logging

from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr

from minaraad.projects.utils import create_attachment
from minaraad.projects.utils import link_project_and_advisory
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
    portal = getToolByName(context, 'portal_url').getPortalObject()
    advisory_folder = portal['adviezen']
    target = portal['digibib']['projects']
    # Only 2009 and younger, so simply take 2009-2011
    for year in ('2009', '2010', '2011'):
        if not base_hasattr(advisory_folder, year):
            continue
        for advisory in advisory_folder[year].contentValues():
            if advisory.portal_type != 'Advisory':
                continue
            if advisory.getProject():
                # This advisory is already linked to a project.
                continue
            # Create a Project.
            project_id = target.generateUniqueId('Project')
            target.invokeFactory('Project', id=project_id)
            project = target[project_id]

            # Determine fields for the Project.
            fields = dict(
                title=advisory.Title(),
                body=advisory.getBody(),
                coordinator=advisory.getCoordinator(),
                authors=advisory.getAuthors(),
                )
            # Some fields needs to be handled separately instead
            # of in the processForm call, as we do not have
            # permission to edit them in a fresh project or the
            # processForm call messes them up (advisory_date would
            # get lost).
            project.setAdvisory_date(advisory.getDate())
            project.setProduct_number(advisory.getProduct_number())
            project.setTheme(advisory.getTheme())
            # Not shown in project, but let's save it anyway:
            project.setEmail_themes(advisory.getEmail_themes())

            # Process the form:
            project.processForm(values=fields)

            # processForm may have caused a rename
            project_id = project.getId()
            # The project_id will actually not be nice because it
            # depends on the internal project id field and we
            # cannot determine that; so we should enable an
            # automatic rename when the object gets edited:
            project.markCreationFlag()
            # Create link between project and advisory
            link_project_and_advisory(project, advisory)
            logger.info("Created a project with id %s.", project_id)

            # The files from the relatedDocuments of the Advisory
            # should become public attachments in the Project.
            related_docs = advisory.getRelatedDocuments()
            related_doc_uids = advisory.getRawRelatedDocuments()
            new_attachments = []
            parent_folders = set()
            for doc in related_docs:
                attachment = create_attachment(project, doc)
                if attachment:
                    parent_folders.add(aq_parent(doc))
                    new_attachments.append(attachment.UID())
            # In advisory point to the new locations.
            advisory.setRelatedDocuments(new_attachments)

            # Look in the the parent folders of the above public
            # documents for any private (or really simply
            # not-linked) files.  Add those as private
            # attachments.  We expect only one folder for each
            # advisory, but do not mind if there are more.
            for parent_folder in parent_folders:
                for doc in parent_folder.contentValues():
                    if doc.UID() in related_doc_uids:
                        continue
                    if (is_advisory_request(doc) and
                        project.getAdvisory_request().getSize() == 0):
                        project.setAdvisory_request(doc.getFile())
                        logger.info("Saved advisory request.")
                    else:
                        create_attachment(project, doc, published=False)

        logger.info("Handled year %s", year)
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
