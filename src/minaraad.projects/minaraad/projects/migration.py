import logging

from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr

from minaraad.projects.utils import create_attachment
from minaraad.projects.utils import datetime_diff_minutes
from minaraad.projects.utils import link_project_and_advisory
from minaraad.projects.utils import is_advisory_request

logger = logging.getLogger('minaraad.projects.migration')
# The default profile id of your package:
PROFILE_ID = 'profile-minaraad.projects:default'


def migrate_agenda_items(context):
    """ Migrates Products.Minaraad.AgendaItem to minaraad.projects.AgendaItem.

    Well, they will still use the Products.Minaraad.AgendaItem class
    but now use the order and duration fields instead of
    getItemstartdate() and getItemenddate().

    Actually, setting the order field is missing here.  We will fix
    that with a second migration.
    """
    try:
        from Products.minaraad.content.AgendaItem import AgendaItem
    except:
        logger.info('Products.minaraad not installed, nothing to migrate ...')
        return

    catalog = context.portal_catalog
    containers = catalog({'portal_type': ['Hearing', 'MREvent']})
    item_count = 0
    migrated_containers = []

    for container in containers:
        container = container.getObject()
        try:
            container.setStart_time(container.getStartdate())
            migrated_containers.append(container)
        except AttributeError:
            pass

        all_items = [o.getObject() for o in
                    catalog({'portal_type': 'AgendaItem',
                             'path': '/'.join(container.getPhysicalPath())})]

        items = sorted(
            [item for item in all_items
             if item.__class__ == AgendaItem and \
                getattr(item, '_migrated_to_new_style_items', None) is None],
            key=lambda x: x.getItemstartdate())

        for item in items:
            item.setDuration(datetime_diff_minutes(item.getItemstartdate(),
                                                   item.getItemenddate()))
            item.reindexObject(['getDuration'])
            item._migrated_to_new_style_items = True

        item_count += len(items)

    logger.info('%s items migrated in %s events (%s migrated)' % (
        item_count,
        len(containers),
        len(migrated_containers)))

    diffs = [(container, container.getEnddate() - container.get_end_time())
             for container in migrated_containers]
    logger.info("The following container's enddate differs from the original "
                "one after migration")
    logger.info(['%s - %sminutes' % (container.absolute_url(),
                                     diff * 1440)
                 for container, diff in diffs
                 if diff])


def correct_order_agenda_items(context):
    """Correct the order of old Products.Minaraad.AgendaItems.

    The previous migration missed setting the order.
    """
    catalog = context.portal_catalog
    containers = catalog({'portal_type': ['Hearing', 'MREvent']})
    item_count = 0
    reordered = 0
    migrated_containers = []
    reordered_containers = []

    for container in containers:
        container = container.getObject()

        all_items = [o.getObject() for o in
                    catalog({'portal_type': 'AgendaItem',
                             'path': '/'.join(container.getPhysicalPath())})]
        # Look for new items that already have a proper order.
        already_ordered_items = sorted([
            item for item in all_items if item.getOrder() is not None],
            key=lambda x: x.getOrder())
        # Look for migrated items without ordering
        items = sorted([item for item in all_items if item.getOrder() is None],
                       key=lambda x: x.getItemstartdate())
        if len(items) > 0:
            logger.info("Container at %s has %d unordered items:",
                         container.absolute_url(), len(items))
            migrated_containers.append(container)
        else:
            # Nothing to do for this container.
            continue
        order = None
        for order, item in enumerate(items):
            item.setOrder(order, recursion=False)
            logger.info("    New order %d: %s", order, item.Title())
        if order is None:
            next_order = 0
        else:
            next_order = order + 1  # This is from the enumerate call.
        if len(already_ordered_items) > 0:
            logger.info("Container at %s has %d already ordered items:",
                        container.absolute_url(), len(already_ordered_items))
            for offset, item in enumerate(already_ordered_items):
                old_order = item.getOrder()
                item.setOrder(next_order, recursion=False)
                logger.info("    Reordered %d -> %d: %s", old_order,
                            next_order, item.Title())
                next_order += 1
                reordered += 1
            reordered_containers.append(container)

        item_count += len(items)

    logger.info("%s items ordered and %d reordered in %s events/hearings "
                "(%s migrated)", item_count, reordered,
                len(containers), len(migrated_containers))
    logger.warn("You may want to check the reordered containers:")
    for container in reordered_containers:
        logger.warn(container.absolute_url())


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
