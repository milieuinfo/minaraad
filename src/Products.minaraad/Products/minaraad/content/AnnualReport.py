from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.CMFCore.permissions import View

from Products.minaraad.interfaces import IAnnualReport
from Products.minaraad import config
from plone.app.blob.field import BlobField

schema = atapi.Schema((

    BlobField(
        name='attachment',
        widget=atapi.FileWidget(
            label='Attachment',
            label_msgid='minaraad_label_attachment',
            i18n_domain='minaraad',
        ),
        storage=atapi.AttributeStorage(),
        searchable=1
    ),

),
)

AnnualReport_schema = atapi.BaseSchema.copy() + schema.copy()


class AnnualReport(atapi.BaseContent):
    """
    An annual report
    """
    implements(IAnnualReport)
    security = ClassSecurityInfo()
    archetype_name = 'AnnualReport'
    portal_type = 'AnnualReport'
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


atapi.registerType(AnnualReport, config.PROJECTNAME)
