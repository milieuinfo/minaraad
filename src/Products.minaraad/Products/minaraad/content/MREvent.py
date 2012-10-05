from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from zope.interface import implements, Interface
from Products.OrderableReferenceField import OrderableReferenceField
from Products.OrderableReferenceField import OrderableReferenceWidget

from minaraad.projects.content.base_meeting import BaseMeeting

from Products.minaraad.config import PROJECTNAME
from Products.minaraad.EmailMixin import EmailMixin
from Products.minaraad.content.interfaces import IUseContact
from Products.minaraad.content.contacts import contacts_schema
from Products.minaraad.content.themes import ThemeMixin
from Products.minaraad.content.themes import theme_schema


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
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword', ),
        widget=atapi.RichWidget(
            label='Goal',
            label_msgid='minaraad_label_goal',
            i18n_domain='minaraad',
            ),
        searchable=1,
        default_content_type='text/html',
        default_output_type='text/html',
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

    atapi.TextField(
        name='body',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword', ),
        widget=atapi.RichWidget(
            label='Body',
            label_msgid='minaraad_label_body',
            i18n_domain='minaraad',
        ),
        searchable=1,
        default_content_type='text/html',
        default_output_type='text/html',
    ),

    atapi.BooleanField(
        name='subscriptionAllowed',
        default=True,
        widget=atapi.BooleanWidget(
            label='Subscription allowed',
            label_msgid='minaraad_label_subscription_allowed',
            description='By default, subscription is allowed till one day before start of the event. Uncheck this field to disallow subscription immediately.',
            description_msgid='minaraad_description_subscription_allowed',
            i18n_domain='minaraad',
        ),
    ),

    atapi.ImageField(
        name='foto',
        widget=atapi.ImageWidget(
            label="Photo",
            label_msgid='minaraad_label_foto',
            i18n_domain='minaraad',
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

    atapi.DateTimeField(
        name='start_time',
        widget=atapi.CalendarWidget(
            label='Startdate',
            label_msgid='minaraad_label_startdate',
            i18n_domain='minaraad',
        ),
        required=1
    ),

),
)

MREvent_schema = atapi.OrderedBaseFolderSchema.copy() + \
    contacts_schema.copy() + \
    getattr(EmailMixin, 'schema', atapi.Schema(())).copy() + \
    theme_schema.copy() + \
    schema.copy()

MREvent_schema.moveField('coordinator', after="foto")
MREvent_schema.moveField('authors', after="coordinator")


class IMREvent(Interface):
    pass


class MREvent(BaseMeeting, EmailMixin, ThemeMixin):
    """
    """
    implements(IMREvent, IUseContact)
    security = ClassSecurityInfo()
    archetype_name = 'MREvent'
    portal_type = 'MREvent'
    _at_rename_after_creation = True
    schema = MREvent_schema


atapi.registerType(MREvent, PROJECTNAME)
