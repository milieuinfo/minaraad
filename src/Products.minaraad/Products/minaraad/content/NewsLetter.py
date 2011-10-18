from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi

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
    security = ClassSecurityInfo()

    # This name appears in the 'add' box
    archetype_name = 'NewsLetter'

    meta_type = 'NewsLetter'
    portal_type = 'NewsLetter'
    allowed_content_types = (
        ['NewsItem'] +
        list(getattr(EmailMixin, 'allowed_content_types', [])))
    filter_content_types = 1
    global_allow = 1
    #content_icon = 'NewsLetter.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "NewsLetter"
    typeDescMsgId = 'description_edit_newsletter'


    _at_rename_after_creation = True

    schema = NewsLetter_schema

    security.declarePublic('getEmailContentsFromContent')
    def getEmailContentsFromContent(self):
        """
        """
        pass


atapi.registerType(NewsLetter, PROJECTNAME)
