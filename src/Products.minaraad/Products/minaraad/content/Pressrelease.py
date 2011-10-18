from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.OrderableReferenceField import OrderableReferenceField
from Products.OrderableReferenceField import OrderableReferenceWidget


from Products.minaraad.Attachmentsmixin import Attachmentsmixin
from Products.minaraad.EmailMixin import EmailMixin
from Products.minaraad.config import PROJECTNAME
from Products.minaraad.content.interfaces import IUseContact
from Products.minaraad.content.contacts import contacts_schema


schema = atapi.Schema((

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
        name='description',
        widget=atapi.TextAreaWidget(
            label='Description',
            label_msgid='minaraad_label_description',
            i18n_domain='minaraad',
        )
    ),

    atapi.DateTimeField(
        name='date',
        widget=atapi.CalendarWidget(
            label='Date',
            label_msgid='minaraad_label_date',
            i18n_domain='minaraad',
        ),
        required=1
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

    atapi.ImageField(
        name='logo_1',
        widget=atapi.ImageWidget(
            label="Logo 1",
            label_msgid='minaraad_label_logo_1',
            i18n_domain='minaraad',
        ),
        storage=atapi.AttributeStorage(),
        sizes={'logo': (125, 125)}
    ),

    atapi.ImageField(
        name='logo_2',
        widget=atapi.ImageWidget(
            label="Logo 2",
            label_msgid='minaraad_label_logo_2',
            i18n_domain='minaraad',
        ),
        storage=atapi.AttributeStorage(),
        sizes={'logo': (125, 125)}
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
        relationship='pressrelease_contact'
    ),
),
)


Pressrelease_schema = (
    getattr(EmailMixin, 'schema', atapi.Schema(())).copy() +
    getattr(Attachmentsmixin, 'schema', atapi.Schema(())).copy() +
    schema.copy() + \
    contacts_schema.copy())

Pressrelease_schema.moveField('coordinator', after="foto")
Pressrelease_schema.moveField('authors', after="coordinator")


class Pressrelease(EmailMixin, Attachmentsmixin):
    """
    A pressrelease
    """
    implements(IUseContact)
    security = ClassSecurityInfo()

    # This name appears in the 'add' box
    archetype_name = 'Pressrelease'

    meta_type = 'Pressrelease'
    portal_type = 'Pressrelease'
    allowed_content_types = (
        list(getattr(EmailMixin, 'allowed_content_types', [])) +
        list(getattr(Attachmentsmixin, 'allowed_content_types', [])))
    filter_content_types = 0
    global_allow = 1
    #content_icon = 'Pressrelease.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Pressrelease"
    typeDescMsgId = 'description_edit_pressrelease'

    _at_rename_after_creation = True

    schema = Pressrelease_schema


atapi.registerType(Pressrelease, PROJECTNAME)
