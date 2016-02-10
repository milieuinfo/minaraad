""" minaraad_type widget
"""
from plone.i18n.normalizer import urlnormalizer as normalizer

from Products.Archetypes.public import Schema
from Products.Archetypes.public import IntegerField
from Products.Archetypes.public import LinesField
from Products.Archetypes.public import IntegerWidget
from Products.Archetypes.public import LinesWidget

from eea.facetednavigation.dexterity_support import normalize as atdx_normalize
from eea.facetednavigation.widgets import ViewPageTemplateFile
from eea.faceted.vocabularies.utils import compare
from eea.facetednavigation.widgets.widget import CountableWidget
from eea.facetednavigation import EEAMessageFactory as _
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


EditSchema = Schema((
    IntegerField(
        'maxitems',
        schemata="display",
        default=0,
        widget=IntegerWidget(
            label=_(u"Maximum items"),
            description=_(u'Number of items visible in widget'),
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
    index_id = 'portal_type'

    def portal_vocabulary(self):
        """Look up selected vocabulary from portal_vocabulary or from ZTK
           zope-vocabulary factory.
        """
        voc_id = 'minaraad.portal_types'
        voc = getUtility(IVocabularyFactory, voc_id)
        values = []
        for term in voc(self.context):
            value = term.value
            if isinstance(value, str):
                value = value.decode('utf-8')
            values.append((value, (term.title or term.token or value)))
        return values

    def vocabulary(self, **kwargs):
        """ Return data vocabulary
        """
        return self.portal_vocabulary()

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
        index = self.index_id
        operator = 'or'

        if self.hidden:
            value = self.default
        else:
            value = form.get(self.data.getId(), '')

        value = atdx_normalize(value)

        if not value:
            return query

        query[index] = {'query': value, 'operator': operator}
        return query

    def count(self, brains, sequence=None):
        """ Intersect results
        """
        # We have removed the index from the fields, because we have a
        # hardcoded index.  But some of the code expects it in the data.
        self.data.index = self.index_id
        return super(Widget, self).count(brains, sequence=sequence)
