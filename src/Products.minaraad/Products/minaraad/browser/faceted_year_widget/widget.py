""" Year widget
"""
import logging

from BTrees.IIBTree import weightedIntersection, IISet
from DateTime import DateTime
from Products.Archetypes.public import IntegerField
from Products.Archetypes.public import IntegerWidget
from Products.Archetypes.public import Schema
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import StringField
from Products.CMFCore.utils import getToolByName
from eea.facetednavigation.interfaces import IFacetedCatalog
from eea.facetednavigation.widgets import ViewPageTemplateFile
from eea.facetednavigation.widgets.widget import CountableWidget \
    as AbstractWidget
from eea.facetednavigation import EEAMessageFactory as _EEA
from Products.minaraad import MinaraadMessageFactory as _
from zope.component import queryUtility

logger = logging.getLogger('mpi.content.browser.faceted_year_widget')

EditSchema = Schema((
    StringField(
        'index',
        schemata="default",
        required=True,
        vocabulary_factory='eea.faceted.vocabularies.DateRangeCatalogIndexes',
        widget=SelectionWidget(
            format='select',
            label=_EEA(u'Catalog index'),
            description=_EEA(u'Catalog index to use for search'),
        )
    ),
    IntegerField(
        'start_year',
        schemata="default",
        required=True,
        default=2000,
        widget=IntegerWidget(
            label=_(u'Start year'),
            description=_(u'Oldest year to start search'),
        )
    ),
    IntegerField(
        'future_years',
        schemata="default",
        required=True,
        default=0,
        widget=IntegerWidget(
            label=_(u'Future years'),
            description=_(u'Number of future years to show'),
        )
    ),
))


class Widget(AbstractWidget):
    """ Widget
    """
    # Widget properties
    widget_type = 'yearrange'
    widget_label = _('Year range')
    view_js = '++resource++minaraad.faceted.year.view.js'
    edit_js = '++resource++minaraad.faceted.year.edit.js'
    # The default css for checkbox widgets seems fine:
    view_css = '++resource++eea.facetednavigation.widgets.checkbox.view.css'
    edit_css = '++resource++eea.facetednavigation.widgets.checkbox.edit.css'
    css_class = 'faceted-year-widget'

    index = ViewPageTemplateFile('widget.pt')
    edit_schema = AbstractWidget.edit_schema.copy() + EditSchema

    @property
    def this_year(self):
        """ Return this year.
        """
        return DateTime().year()

    @property
    def years(self):
        this_year = self.this_year
        try:
            future = int(self.data.get('future_years', 0))
        except (ValueError, TypeError):
            future = 0
        try:
            start = int(self.data.get('start_year')) - 1
        except (ValueError, TypeError):
            start = this_year - 6
        # Return [2014, 2013, 2012, ...]
        return range(this_year + future, start, -1)

    def count(self, brains, sequence=None):
        """ Intersect results
        """
        res = {}
        if not sequence:
            sequence = self.years

        if not sequence:
            return res

        index_id = self.data.get('index')
        if not index_id:
            return res

        ctool = getToolByName(self.context, 'portal_catalog')
        index = ctool._catalog.getIndex(index_id)
        ctool = queryUtility(IFacetedCatalog)
        if not ctool:
            return res

        brains = IISet(brain.getRID() for brain in brains)
        res[""] = res['all'] = len(brains)
        for value in sequence:
            if not value:
                res[value] = len(brains)
                continue
            year = int(value)
            start = DateTime(year, 1, 1)
            end = DateTime(year, 12, 31).latestTime()
            query = {
                'query': (start, end),
                'range': 'min:max'
            }
            rset = ctool.apply_index(self.context, index, query)[0]
            rset = IISet(rset)
            rset = weightedIntersection(brains, rset)[1]
            res[value] = len(rset)
        return res

    def query(self, form):
        """ Get value from form and return a catalog dict query
        """
        query = {}
        index = self.data.get('index', '')
        index = index.encode('utf-8', 'replace')
        if not index:
            return query

        if self.hidden:
            years = [self.this_year]
        else:
            years = form.get(self.data.getId(), [])
            if not isinstance(years, list):
                years = [years]
        try:
            years = [int(year) for year in years]
        except (ValueError, TypeError):
            years = []
        if not years:
            return query

        # The date indexes do not support selecting for example year
        # 2011 and 2014, as far as I can see.  So we make a range from
        # first to last.
        years = sorted(years)
        start_year = years[0]
        end_year = years[-1]
        start = DateTime(start_year, 1, 1)
        end = DateTime(end_year, 12, 31).latestTime()
        query[index] = {
            'query': (start, end),
            'range': 'min:max'
        }
        return query
