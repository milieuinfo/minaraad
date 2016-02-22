from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.OrderableReferenceField import OrderableReferenceField
from Products.OrderableReferenceField import OrderableReferenceWidget

from Products.minaraad.config import PROJECTNAME
from Products.minaraad.content.interfaces import IUseContact
from Products.minaraad.content.contacts import contacts_schema
from Products.minaraad.interfaces import INewsItem


schema = atapi.Schema((

    atapi.StringField(
        name='category',
        widget=atapi.SelectionWidget(
            label='Category',
            label_msgid='minaraad_label_category',
            i18n_domain='minaraad',
        ),
        vocabulary=["Vastgestelde adviezen",
                    "Adviezen in wording",
                    "Mededelingen",
                    "Europese ontwikkelingen"]
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
        default_output_type='text/x-html-safe',
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
        relationship='newsitem_contact'
    ),

),
)

NewsItem_schema = atapi.BaseSchema.copy() + schema.copy() + \
    contacts_schema.copy()


class NewsItem(atapi.BaseContent):
    """
    """
    implements(IUseContact, INewsItem)
    security = ClassSecurityInfo()
    archetype_name = 'NewsItem'
    portal_type = 'NewsItem'
    _at_rename_after_creation = True
    schema = NewsItem_schema


atapi.registerType(NewsItem, PROJECTNAME)
