from Products.Archetypes import atapi
from Products.OrderableReferenceField import OrderableReferenceField
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget

contacts_schema = atapi.Schema((
    atapi.ReferenceField(
        name='coordinator',
        relationship='coordinator',
        multiValued=0,
        languageIndependent=1,
        allowed_types=('ContactPerson', ),
        widget=ReferenceBrowserWidget(
            label='Coordinator',
            label_msgid='minaraad_label_coordinator',
            i18n_domain='minaraad',
            startup_directory='/contactpersonen',
            restrict_browsing_to_startup_directory=0,
            show_review_state=1,
            allow_search=1,
            allow_browse=1,
            show_indexes=0,
            force_close_on_insert=1,
            base_query={
                'sort_on': 'sortable_title',
            },
        ),
    ),

    OrderableReferenceField(
        name='authors',
        vocabulary_display_path_bound="-1",
        widget=ReferenceBrowserWidget(
            label='co-authors',
            label_msgid='minaraad_label_authors',
            i18n_domain='minaraad',
            startup_directory='/contactpersonen',
            restrict_browsing_to_startup_directory=0,
            show_review_state=1,
            allow_search=1,
            allow_browse=1,
            show_indexes=0,
            force_close_on_insert=0,
            multivalued=1,
            base_query={
                'sort_on': 'sortable_title',
            },
        ),
        allowed_types=('ContactPerson', ),
        multiValued=1,
        relationship='authors'
    ),
))
