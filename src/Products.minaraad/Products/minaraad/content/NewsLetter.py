from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi

from Products.minaraad.interfaces import INewsLetter
from Products.minaraad.EmailMixin import EmailMixin
from Products.minaraad.config import PROJECTNAME


schema = atapi.Schema((

    atapi.TextField(
        name='description',
        widget=atapi.TextAreaWidget(
            label='Description',
            label_msgid='minaraad_label_description',
            i18n_domain='minaraad',
        )
    ),

    atapi.DateTimeField(
        name='date',
        required=True,
        widget=atapi.CalendarWidget(
            label='Date',
            label_msgid='minaraad_label_date',
            i18n_domain='minaraad',
        )
    ),

    atapi.TextField(
        name='body',
        allowable_content_types=('text/plain', 'text/structured', 'text/html',
                                 'application/msword'),
        widget=atapi.RichWidget(
            label='Body',
            label_msgid='minaraad_label_body',
            i18n_domain='minaraad',
        ),
        default_content_type='text/html',
        default_output_type='text/html',
    ),

),
)


NewsLetter_schema = atapi.OrderedBaseFolderSchema.copy() + \
    getattr(EmailMixin, 'schema', atapi.Schema(())).copy() + \
    schema.copy()


class NewsLetter(EmailMixin, atapi.OrderedBaseFolder):
    """
    A newsletter
    """
    implements(INewsLetter)
    security = ClassSecurityInfo()
    archetype_name = 'NewsLetter'
    portal_type = 'NewsLetter'
    _at_rename_after_creation = True
    schema = NewsLetter_schema

    security.declarePublic('getEmailContentsFromContent')

    def getEmailContentsFromContent(self):
        """
        """
        pass


atapi.registerType(NewsLetter, PROJECTNAME)
