""" minaraad_type widget
"""
from plone.i18n.normalizer import urlnormalizer as normalizer

from Products.Archetypes.public import Schema
from Products.Archetypes.public import IntegerField
from Products.Archetypes.public import LinesField
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import StringField
from Products.Archetypes.public import IntegerWidget
from Products.Archetypes.public import LinesWidget
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import BooleanWidget
from Products.CMFCore.utils import getToolByName

from eea.facetednavigation.dexterity_support import normalize as atdx_normalize
from eea.facetednavigation.widgets import ViewPageTemplateFile
from eea.faceted.vocabularies.utils import compare
from eea.facetednavigation.widgets.widget import CountableWidget
from eea.facetednavigation import EEAMessageFactory as _


EditSchema = Schema((
    StringField(
        'vocabulary',
        schemata="default",
        vocabulary_factory='eea.faceted.vocabularies.PortalVocabularies',
        widget=SelectionWidget(
            label=_(u"Vocabulary"),
            description=_(u'Vocabulary to use to render widget items'),
        )
    ),
    StringField(
        'catalog',
        schemata="default",
        vocabulary_factory='eea.faceted.vocabularies.UseCatalog',
        widget=SelectionWidget(
            format='select',
            label=_(u'Catalog'),
            description=_(u"Get unique values from catalog "
                          u"as an alternative for vocabulary"),
        )
    ),
    IntegerField(
        'maxitems',
        schemata="display",
        default=0,
        widget=IntegerWidget(
            label=_(u"Maximum items"),
            description=_(u'Number of items visible in widget'),
        )
    ),
    BooleanField(
        'sortreversed',
        schemata="display",
        widget=BooleanWidget(
            label=_(u"Reverse options"),
            description=_(u"Sort options reversed"),
        )
    ),
    LinesField(
        'default',
        schemata="default",
        widget=LinesWidget(
            label=_(u'Default value'),
            description=_(u'Default items (one per line)'),
            i18n_domain="eea"
        )
    ),
))


class Widget(CountableWidget):
    """ Widget
    """
    # Widget properties
    widget_type = 'minaraad_type'
    widget_label = _('Types')
    view_js = '++resource++eea.facetednavigation.widgets.minaraad_type.view.js'
    edit_js = '++resource++eea.facetednavigation.widgets.minaraad_type.edit.js'
    view_css = '++resource++eea.facetednavigation.widgets.minaraad_type.view.css'  # noqa
    edit_css = '++resource++eea.facetednavigation.widgets.minaraad_type.edit.css'  # noqa

    index = ViewPageTemplateFile('widget.pt')
    edit_schema = CountableWidget.edit_schema.copy() + EditSchema

    @property
    def css_class(self):
        """ Widget specific css class
        """
        css_type = self.widget_type
        css_title = normalizer.normalize(self.data.title)
        return ('faceted-minaraad-types-widget '
                'faceted-{0}-widget section-{1}').format(css_type, css_title)

    @property
    def default(self):
        """ Get default values
        """
        default = super(Widget, self).default
        if not default:
            return []

        if isinstance(default, (str, unicode)):
            default = [default, ]
        return default

    def selected(self, key):
        """ Return True if key in self.default
        """
        default = self.default
        if not default:
            return False
        for item in default:
            if compare(key, item) == 0:
                return True
        return False

    @property
    def operator_visible(self):
        """ Is operator visible for anonymous users
        """
        return False

    @property
    def operator(self):
        """ Get the default query operator
        """
        return 'or'

    def query(self, form):
        """ Get value from form and return a catalog dict query
        """
        query = {}
        index = 'portal_type'
        operator = 'or'

        if self.hidden:
            value = self.default
        else:
            value = form.get(self.data.getId(), '')

        value = atdx_normalize(value)

        if not value:
            return query

        catalog = getToolByName(self.context, 'portal_catalog')
        if catalog.Indexes[index].meta_type == 'BooleanIndex':
            if value == 'False':
                value = False
            elif value == 'True':
                value = True

        query[index] = {'query': value, 'operator': operator}
        return query
