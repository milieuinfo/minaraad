""" Checkbox widget
"""
from BTrees.IIBTree import weightedIntersection, IISet
from eea.facetednavigation import EEAMessageFactory as _
from eea.facetednavigation.dexterity_support import normalize as atdx_normalize
from eea.facetednavigation.interfaces import IFacetedCatalog
from eea.facetednavigation.widgets import ViewPageTemplateFile
from eea.facetednavigation.widgets.widget import CountableWidget
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility
from plone import api


EditSchema = Schema((

    BooleanField('hidealloption',
        schemata="default",
        default=False,
        widget=BooleanWidget(
            label=_(u"Hide 'All' option"),
            description=_(u'If this checkbox is checked, hides the All '
                          u'option'),
            i18n_domain="eea"
        )
    ),

    StringField('default',
        schemata="default",
        widget=StringWidget(
            size=25,
            label=_(u'Default value'),
            description=_(u'Default selected item'),
            i18n_domain="eea"
        )
    ),

))


class Widget(CountableWidget):
    """ Widget
    """
    # Widget properties
    widget_type = 'section'
    widget_label = _('Section')
    view_js = '++resource++eea.facetednavigation.widgets.section.view.js'
    edit_js = '++resource++eea.facetednavigation.widgets.section.edit.js'
    view_css = '++resource++eea.facetednavigation.widgets.section.view.css'

    index = ViewPageTemplateFile('widget.pt')
    edit_schema = CountableWidget.edit_schema.copy() + EditSchema

    def vocabulary(self):
        return [
            ('other', 'Website'),
            ('digibib', 'Digibib'),
        ]

    def section_to_path(self, value):
        portal = api.portal.get()
        site_id = portal.getId()
        if value == "digibib":
            return '/%s/digibib' % site_id
        if value == "other":
            paths = []
            for brain in api.content.find(portal, depth=1):
                if brain.portal_type != 'DigiBib':
                    paths.append(brain.getPath())
            return paths
        return ''

    def count(self, brains, sequence=None):
        """ Intersect results
        """
        res = {}
        # by checking for facet_counts we assume this is a SolrResponse
        # from collective.solr
        if hasattr(brains, 'facet_counts'):
            facet_fields = brains.facet_counts.get('facet_fields')
            if facet_fields:
                index_id = self.data.get('index')
                facet_field = facet_fields.get(index_id, {})
                for value, num in facet_field.items():
                    normalized_value = atdx_normalize(value)
                    if isinstance(value, unicode):
                        res[value] = num
                    elif isinstance(normalized_value, unicode):
                        res[normalized_value] = num
                    else:
                        unicode_value = value.decode('utf-8')
                        res[unicode_value] = num
            else:
                # no facet counts were returned. we exit anyway because
                # zcatalog methods throw an error on solr responses
                return res
            res[""] = res['all'] = len(brains)
            return res
        else:
            # this is handled by the zcatalog. see below
            pass

        if not sequence:
            sequence = [key for key, value in self.vocabulary()]

        if not sequence:
            return res

        index_id = 'path'
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
            normalized_value = self.section_to_path(value)
            rset = ctool.apply_index(self.context, index, normalized_value)[0]
            rset = IISet(rset)
            rset = weightedIntersection(brains, rset)[1]
            if isinstance(value, unicode):
                res[value] = len(rset)
            elif isinstance(normalized_value, unicode):
                res[normalized_value] = len(rset)
            else:
                unicode_value = value.decode('utf-8')
                res[unicode_value] = len(rset)
        return res

    def query(self, form):
        """ Get value from form and return a catalog dict query
        """
        query = {}

        if self.hidden:
            value = self.default
        else:
            value = form.get(self.data.getId(), '')

        if value:
            path = self.section_to_path(value)
            if path:
                query['path'] = path

        return query
