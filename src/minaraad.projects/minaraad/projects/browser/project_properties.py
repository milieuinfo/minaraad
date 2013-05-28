from zope.i18n import translate
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from minaraad.projects.config import FILTERED_GROUPS
from minaraad.projects import MinaraadProjectMessageFactory as _


class ProjectPropertiesView(BrowserView):
    """ Minaraad properties linked to the
    project managment.
    """

    def __init__(self, *args, **kwargs):
        super(ProjectPropertiesView, self).__init__(*args, **kwargs)
        self.errors = []

    def add_portal_message(self, msg, type='info'):
        """ Translates the message and displays it as a
        portal message.
        """
        translated = translate(msg, context=self.request)
        IStatusMessage(self.request).addStatusMessage(translated, type)

    def _get_minaraad_properties(self):
        portal_props = getToolByName(self.context, 'portal_properties')
        return portal_props.minaraad_properties

    def get_properties(self):
        props = self._get_minaraad_properties()
        return {'email': props.secretary_email,
                'board': props.governance_board,
                'requesters': '\n'.join(props.requesters),
                'membership_organizations': '\n'.join(
                    props.membership_organizations),
                }

    def set_properties(self, email, board, requesters,
                       membership_organizations):
        props = self._get_minaraad_properties()
        props.secretary_email = email
        props.governance_board = board
        props.requesters = requesters
        props.membership_organizations = membership_organizations

    def get_groups(self):
        pgroups = getToolByName(self.context, 'portal_groups')
        return sorted([g.id for g in pgroups.listGroups()
                       if not g.id in FILTERED_GROUPS])

    def __call__(self):
        form = self.request.form

        if 'form_cancelled' in form:
            self.add_portal_message(
                _(u'label_project_props_canceled',
                  default=u'Changes have been cancelled'))

            return self.index()

        if not 'form_submitted' in form:
            return self.index()

        if not form.get('email', None):
            self.errors.append('email')

        if not form.get('board', None):
            self.errors.append('board')

        if not self.errors:
            self.set_properties(form.get('email'),
                                form.get('board'),
                                form.get('requesters'),
                                form.get('membership_organizations'),
                                )
            self.add_portal_message(
                _(u'label_project_props_saved',
                  default=u'Project properties have been saved'))
        else:
            self.add_portal_message(
                _(u'label_project_props_error',
                  default=(u"Errors have been found while processing the "
                           u"form, please correct them")),
                'error')

        return self.index()
