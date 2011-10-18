from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.CMFCore.permissions import View

from Products.minaraad.PostMixin import PostMixin
from Products.minaraad.EmailMixin import EmailMixin
from Products.minaraad.config import *


schema = Schema((

    FileField(
        name='attachment',
        widget=FileWidget(
            label='Attachment',
            label_msgid='minaraad_label_attachment',
            i18n_domain='minaraad',
        ),
        storage=AttributeStorage(),
        searchable=1
    ),

),
)

AnnualReport_schema = BaseSchema.copy() + \
    getattr(PostMixin, 'schema', Schema(())).copy() + \
    getattr(EmailMixin, 'schema', Schema(())).copy() + \
    schema.copy()


class AnnualReport(PostMixin, EmailMixin, BaseContent):
    """
    An annual report
    """
    security = ClassSecurityInfo()

    # This name appears in the 'add' box
    archetype_name = 'AnnualReport'

    meta_type = 'AnnualReport'
    portal_type = 'AnnualReport'
    allowed_content_types = list(getattr(PostMixin, 'allowed_content_types', [])) + list(getattr(EmailMixin, 'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 1
    #content_icon = 'AnnualReport.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "AnnualReport"
    typeDescMsgId = 'description_edit_annualreport'
    _at_rename_after_creation = True

    schema = AnnualReport_schema

    security.declareProtected(View, 'download')
    def download(self, REQUEST=None, RESPONSE=None):
        """Download the file (with content-disposition attachment).
        """
        if REQUEST is None:
            REQUEST = self.REQUEST
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE
        field = self.getField('attachment')
        return field.download(self, REQUEST, RESPONSE)


registerType(AnnualReport, PROJECTNAME)
