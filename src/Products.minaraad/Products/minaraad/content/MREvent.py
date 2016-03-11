from AccessControl import ClassSecurityInfo
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.Archetypes import atapi
from Products.OrderableReferenceField import OrderableReferenceField
from Products.OrderableReferenceField import OrderableReferenceWidget
from Products.minaraad.config import PROJECTNAME
from Products.minaraad.content.contacts import contacts_schema
from Products.minaraad.content.interfaces import IUseContact
from Products.minaraad.ThemeMixin import ThemeParentMixin
from Products.minaraad.interfaces import IMREvent
from Products.minaraad.Attachmentsmixin import Attachmentsmixin
from Products.minaraad.ImageAttachmentsmixin import ImageAttachmentsmixin
from minaraad.projects.content.base_meeting import BaseMeeting
from plone.app.blob.field import ImageField
from zope.interface import implements


schema = atapi.Schema((

    atapi.TextField(
        name='description',
        widget=atapi.TextAreaWidget(
            label='Description',
            label_msgid='minaraad_label_description',
            i18n_domain='minaraad',
        )
    ),

    atapi.StringField(
        name='subheader',
        widget=atapi.StringWidget(
            label='Subheader',
            label_msgid='minaraad_label_subheader',
            i18n_domain='minaraad',
        ),
        searchable=1
    ),

    atapi.TextField(
        name='goal',
        allowable_content_types=('text/html', 'text/plain'),
        widget=atapi.RichWidget(
            label='Goal',
            label_msgid='minaraad_label_goal',
            i18n_domain='minaraad',
        ),
        searchable=1,
        default_content_type='text/html',
        default_output_type='text/x-html-safe',
    ),

    atapi.StringField(
        name='location',
        widget=atapi.StringWidget(
            label='Location',
            label_msgid='minaraad_label_location',
            i18n_domain='minaraad',
        ),
        searchable=1
    ),

    atapi.DateTimeField(
        name='start_time',
        widget=atapi.CalendarWidget(
            label='Startdate',
            label_msgid='minaraad_label_startdate',
            i18n_domain='minaraad',
        ),
        required=1
    ),

    atapi.TextField(
        name='body',
        allowable_content_types=('text/html', 'text/plain'),
        widget=atapi.RichWidget(
            label='Body',
            label_msgid='minaraad_label_body',
            i18n_domain='minaraad',
        ),
        searchable=1,
        default_content_type='text/html',
        default_output_type='text/x-html-safe',
    ),

    atapi.BooleanField(
        name='subscriptionAllowed',
        default=True,
        widget=atapi.BooleanWidget(
            label='Subscription allowed',
            label_msgid='minaraad_label_subscription_allowed',
            description=(
                'By default, subscription is allowed till one day before '
                'start of the event. Uncheck this field to disallow '
                'subscription immediately.'),
            description_msgid='minaraad_description_subscription_allowed',
            i18n_domain='minaraad',
        ),
    ),

    ImageField(
        name='foto',
        widget=atapi.ImageWidget(
            label="Photo",
            label_msgid='minaraad_label_foto',
            i18n_domain='minaraad',
            visible=False
        ),
        storage=atapi.AttributeStorage(),
        sizes={'foto': (300, 300)}
    ),

    OrderableReferenceField(
        name='contact',
        vocabulary_display_path_bound="-1",
        widget=OrderableReferenceWidget(
            visible=False,
            label='Contact',
            label_msgid='minaraad_label_contact',
            i18n_domain='minaraad',
        ),
        allowed_types=('ContactPerson', ),
        multiValued=1,
        relationship='mrevent_contact'
    ),

    atapi.ReferenceField(
        name='relatedDocuments',
        vocabulary_display_path_bound="-1",
        widget=ReferenceBrowserWidget(
            label='Related Documents',
            label_msgid='minaraad_label_related_documents',
            description="Related and published digibib documents and files",
            description_msgid="minaraad_help_related_documents",
            i18n_domain='minaraad',
            # ATReferenceBrowser specific additions:
            startup_directory='/',
            restrict_browsing_to_startup_directory=0,
            only_for_review_states=('published', ),
            show_review_state=1,
            allow_search=1,
            allow_browse=1,
            show_indexes=0,
            force_close_on_insert=0,
        ),
        allowed_types=('Document', 'File', 'FileAttachment',
                       'Advisory', 'Study', 'MREvent'),
        multiValued=True,
        relationship='related_documents'
    ),

),
)

MREvent_schema = atapi.OrderedBaseFolderSchema.copy() + \
    schema.copy() + \
    ImageAttachmentsmixin.schema.copy() + \
    contacts_schema.copy()

MREvent_schema.moveField('coordinator', after="subscriptionAllowed")
MREvent_schema.moveField('authors', after="coordinator")


class MREvent(Attachmentsmixin, BaseMeeting, ThemeParentMixin):
    """
    """
    implements(IMREvent, IUseContact)
    security = ClassSecurityInfo()
    archetype_name = 'MREvent'
    portal_type = 'MREvent'
    _at_rename_after_creation = True
    schema = MREvent_schema


atapi.registerType(MREvent, PROJECTNAME)
