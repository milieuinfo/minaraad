from archetypes.referencebrowserwidget import ReferenceBrowserWidget
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.permissions import ModifyPortalContent
from Products.minaraad.config import PROJECTNAME
from Products.minaraad.interfaces import ITheme
from Products.validation import V_REQUIRED
from zope.interface import implements

ThemeSchema = folder.ATFolderSchema.copy() + atapi.Schema((

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
        "image",
        original_size=(600, 600),
        sizes={
            'mini': (80, 80),
            'normal': (200, 200),
            'big': (300, 300),
            'maxi': (500, 500),
        },
        validators=(
            ('isNonEmptyFile', V_REQUIRED),
            ('checkImageMaxSize', V_REQUIRED)
        ),
        widget=atapi.ImageWidget(
            label="Thema icoon",
            description=("Upload een vierkante afbeelding "
                         "(een detail uit de footer afbeelding)"),
            show_content_type=False,
        ),
    ),

    atapi.ImageField(
        "footerImage",
        original_size=(1200, 300),
        sizes={
            'mini': (80, 80),
            'normal': (200, 200),
            'big': (300, 300),
            'maxi': (1500, 500),
        },
        validators=(
            ('isNonEmptyFile', V_REQUIRED),
            ('checkImageMaxSize', V_REQUIRED)
        ),
        widget=atapi.ImageWidget(
            label="Footer afbeelding",
            description=("Upload een liggende afbeelding, "
                         "ongeveer drie keer zo breed als hoog, "
                         "bijvoorbeeld 1500 pixels breed by 500 pixels hoog."),
            show_content_type=False,
        ),
    ),

    atapi.ReferenceField(
        'highlighted',
        relationship='relatesTo',
        multiValued=True,
        isMetadata=True,
        languageIndependent=False,
        referencesSortable=True,
        keepReferencesOnCopy=True,
        write_permission=ModifyPortalContent,
        widget=ReferenceBrowserWidget(
            allow_search=True,
            allow_browse=True,
            allow_sorting=True,
            show_indexes=False,
            force_close_on_insert=True,
            label=u'Related items',
            description='',
            visible={'edit': 'visible', 'view': 'invisible'}
        )
    ),

    atapi.BooleanField(
        "secondary",
        widget=atapi.BooleanWidget(
                description="Als aangevinkt zal deze folder uitgesloten worden van primaire lijstjes en alleen voorkomen in de secondaire thema lijsten.",
        )
    ),

))

ThemeSchema['title'].widget.label = u"Themanaam"
ThemeSchema['title'].widget.description = u""
ThemeSchema['description'].widget.label = u"Inleiding"
ThemeSchema['description'].widget.description = u"Korte uitleg over wat dit thema behelst."
finalizeATCTSchema(
        ThemeSchema,
        folderish=True,
        moveDiscussion=False
)


class Theme(folder.ATFolder):
    """Describe a Theme.

    This is a folder. It groups items per theme.
    """

    implements(ITheme)
    schema = ThemeSchema

    def getThemeTitle(self):
        """Return the title of the Theme in which this Advisory resides"""
        return self.Title()


atapi.registerType(Theme, PROJECTNAME)
