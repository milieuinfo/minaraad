""" Select widget
"""
from BTrees.IIBTree import weightedIntersection, IISet
from DateTime import DateTime
from eea.facetednavigation import EEAMessageFactory as _
from eea.facetednavigation.interfaces import IFacetedCatalog
from eea.facetednavigation.widgets import ViewPageTemplateFile
from eea.facetednavigation.widgets.widget import CountableWidget
from Products.Archetypes.public import Schema
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility


EditSchema = Schema(())


class Widget(CountableWidget):
    """ Widget
    """
    # Widget properties
    widget_type = 'year-select'
    widget_label = _('Year select')
    view_js = '++resource++eea.facetednavigation.widgets.year-select.view.js'
    edit_js = '++resource++eea.facetednavigation.widgets.year-select.edit.js'
    view_css = '++resource++eea.facetednavigation.widgets.year-select.view.css'

    index = ViewPageTemplateFile('widget.pt')
    edit_schema = CountableWidget.edit_schema.copy() + EditSchema

    def default(self):
        return ""

    @property
    def years(self):

        catalog = getToolByName(self.context, 'portal_catalog')

        # Sometimes objects are created with a effective date of
        # '1000-01-01 00:00:00'. Resulting in 1000+ values.
        # Therefore we limit `first` to a reasonable effective date.
        first = catalog.searchResults(
                sort_on='effective',
                sort_order='ascending',
                sort_limit=1,
                effective={
                    'query': (
                        DateTime('1980-01-01 00:00:00'),
                    ),
                    'range': 'min',
                }
        )[0].effective.year()
        last = catalog.searchResults(
                sort_on='effective',
                sort_order='descending',
                sort_limit=1
        )[0].effective.year()

        years = range(first, last + 1, 1)
        years.reverse()
        return years

    def vocabulary(self):
        years = self.years
        return [(str(i), str(i)) for i in years]

    def count(self, brains, sequence=None):
        """ Intersect results
        """
        res = {}
        if not sequence:
            sequence = self.years

        if not sequence:
            return res

        index_id = 'effective'
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

        if self.hidden:
            value = self.default
        else:
            value = int(form.get(self.data.getId(), 0))

        if not value:
            return query
        # The date indexes do not support selecting for example year.
        # So we make a range from first to last day of the year.
        start = DateTime(value, 1, 1)
        end = DateTime(value, 12, 31).latestTime()
        query['effective'] = {
            'query': (start, end),
            'range': 'min:max'
        }
        return query
