from Acquisition import aq_inner
from minaraad.projects import MinaraadProjectMessageFactory as _
from minaraad.projects.utils import link_project_and_advisory
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

import logging


logger = logging.getLogger(__name__)


class CanCreateAdvisory(BrowserView):
    """Can this user create an Advisory from the current Project?

    Note that this view MUST be available on all items, as this will
    be referenced from portal_actions/object_buttons/create_advisory.
    """

    @property
    def base_target(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        if not base_hasattr(portal, 'themas'):
            logger.warn("Target folder 'themas' not found.")
            return None
        return portal.themas

    def available(self):
        """Is the action available?
        """
        context = aq_inner(self.context)
        if not base_hasattr(context, 'portal_type'):
            return False
        if context.portal_type != 'Project':
            return False
        wf_tool = getToolByName(context, 'portal_workflow')
        if wf_tool.getInfoFor(context, 'review_state') != 'completed':
            return False
        mtool = getToolByName(context, 'portal_membership')
        if not mtool.checkPermission('Copy or Move', context):
            return False
        if not self.base_target:
            return False
        if context.get_public_advisory():
            # We already have one.
            return False
        # This should match the permission needed to add an Advisory,
        # which in our case is the default add permission:
        if not mtool.checkPermission('Add portal content', self.base_target):
            return False
        return True

    def __call__(self):
        """Can we do it?
        """
        return self.available()


class CreateAdvisory(CanCreateAdvisory):

    def __call__(self):
        """Perform the action.
        """
        if not self.available():
            # Should Not Happen (TM)
            return u"Sorry, this page is not available."

        # Some definitions
        context = aq_inner(self.context)
        add_message = IStatusMessage(self.request).addStatusMessage
        catalog = getToolByName(context, 'portal_catalog')

        # We add the advisory in a theme.
        path = context.getTheme_path()
        if not path:
            add_message(_(u"No theme set on project."), type='error')
            return self.request.RESPONSE.redirect(context.absolute_url())
        try:
            target = context.restrictedTraverse(path)
        except AttributeError:
            add_message(_(u"Cannot find theme that is set on project."),
                        type='error')
            return self.request.RESPONSE.redirect(context.absolute_url())

        # Create an Advisory in there.
        advisory_id = target.generateUniqueId('Advisory')
        target.invokeFactory('Advisory', id=advisory_id)
        advisory = target[advisory_id]

        # Get the public attachments from the Project.
        public_uids = [x.UID for x in catalog.searchResults(
            path='/'.join(context.getPhysicalPath()),
            review_state='published')]

        # Determine fields for the Advisory.
        fields = dict(
            title=context.Title(),
            coordinator=context.getCoordinator(),
            authors=context.getAuthors(),
            product_number=context.getProduct_number(),
            relatedDocuments=public_uids,
        )

        # For some reason the date field needs to be handled separately.
        advisory.setDate(context.getDelivery_date())
        # Process the form.
        advisory.processForm(values=fields)

        # processForm may have caused a rename
        advisory_id = advisory.getId()
        # Create link between project and advisory
        link_project_and_advisory(context, advisory)
        logger.info("Created an advisory with id %s.", advisory_id)

        # Add a status message.
        add_message(_(u"Created Advisory"), type='info')

        # Redirect to that Advisory.
        self.request.RESPONSE.redirect(advisory.absolute_url())


class ProjectView(BrowserView):
    """ Default view of a Project.
    """

    def get_attachments(self):
        catalog = getToolByName(self.context,
                                'portal_catalog')
        first_level = catalog.searchResults(
            path={'query': '/'.join(self.context.getPhysicalPath()),
                  'depth': 1},
            sort_on='getObjPositionInParent')

        return first_level

    def can_see_project_number(self):
        """ Returns a boolean telling if the user
        can see the project number.
        """
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission('minaraad.projects: view project id',
                                     self.context)


class ProjectDocumentsView(BrowserView):
    """ View to display all discussed documents
    for the projects.
    """

    def get_data(self):
        """ Returns a list of dictionnary:
        {'meeting': a meeting object,
         'items': a list of items related to the project}
        """

        meetings = self.context.get_agenda_items()
        res = []
        catalog = getToolByName(self.context, 'portal_catalog')

        for meeting in sorted(meetings, key=lambda x: x.getStart_time()):
            items = sorted([i for i in meetings[meeting]
                            if catalog(
                                {'path': '/'.join(i.getPhysicalPath()),
                                 'portal_type': 'FileAttachment'})],
                           key=lambda x: x.getOrder())

            if items:
                res.append({'meeting': meeting,
                            'items': items})
        return res
