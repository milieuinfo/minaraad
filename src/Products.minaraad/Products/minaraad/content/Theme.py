from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.minaraad.config import PROJECTNAME
from Products.minaraad.interfaces import ITheme
from zope.interface import implements
from Products.validation import V_REQUIRED

ThemeSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # atapi.StringField(
    #         'phone',
    #         required=True,
    #         searchable=True,
    #         widget=atapi.StringWidget(
    #                 label="Phone number",
    #                 description=""
    #         )
    # ),
    #
    # atapi.TextField(
    #         'text',
    #         required=False,
    #         searchable=True,
    #         validators=('isTidyHtmlWithCleanup',),
    #         default_output_type='text/x-html-safe',
    #         widget=atapi.RichWidget(
    #                 label=u"Descriptive text",
    #                 description="",
    #                 rows=25,
    #                 allow_file_upload=False
    #         ),
    # ),
    # atapi.ReferenceField(
    #         'highlightedFilms',
    #         relationship='isPromotingFilm',
    #         multiValued=True,
    #         vocabulary_factory=u"optilux.cinemacontent.CurrentFilms",
    #         vocabulary_display_path_bound=-1,
    #         enforceVocabulary=True,
    #         widget=atapi.ReferenceWidget(
    #                 label="Highlighted films",
    #                 description=""
    #         )
    # ),

    atapi.ImageField(
        "image",
        original_size=(600, 600),
        # sizes={
        #     'mini': (80,80),
        #     'normal': (200,200),
        #     'big': (300,300),
        #     'maxi': (500,500)
        # }
        validators=(
            ('isNonEmptyFile', V_REQUIRED),
            ('checkImageMaxSize', V_REQUIRED)
        ),
        widget=atapi.ImageWidget(
                label="Thema icoon",
                desciption="Upload een vierkante afbeelding (een detail uit de footer-afbeelding)",
                show_content_type=False,
        ),
    ),

    atapi.ImageField(
        "footerImage",
        original_size=(1200, 600),
        # sizes={
        #     'mini': (80,80),
        #     'normal': (200,200),
        #     'big': (300,300),
        #     'maxi': (500,500)
        # }
        validators=(
            ('isNonEmptyFile', V_REQUIRED),
            ('checkImageMaxSize', V_REQUIRED)
        ),
        widget=atapi.ImageWidget(
                label="Thema icoon",
                desciption="Upload een vierkante afbeelding (een detail uit de footer-afbeelding)",
                show_content_type=False,
        ),
    ),

    atapi.BooleanField(
        "secondary",
        widget=atapi.BooleanWidget(
                description="Als aangevinkt zal deze folder uitgesloten worden van primaire lijstjes en alleen voorkomen in de secondaire thema lijsten.",
        )
    ),

    atapi.IntegerField(
            'migrationId',
            required=False,
            searchable=False,
            widget=atapi.IntegerWidget(
                    label="Old theme id",
                    description="This id is used to select this folder in a upgrade step for theme mapping."
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

atapi.registerType(Theme, PROJECTNAME)
