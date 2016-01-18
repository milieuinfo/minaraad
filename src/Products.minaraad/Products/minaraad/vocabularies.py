from binascii import b2a_qp
from eea.faceted.vocabularies.utils import compare
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.site.hooks import getSite
import operator


def safe_encode(term):
    if not isinstance(term, basestring):
        term = str(term)
    if isinstance(term, unicode):
        # no need to use portal encoding for transitional encoding from
        # unicode to ascii. utf-8 should be fine.
        term = term.encode('utf-8')
    return term


class ThemePathVocabulary(object):
    """Vocabulary listing paths of Themes.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        site = getSite()
        catalog = getToolByName(site, "portal_catalog", None)
        if catalog is None:
            return SimpleVocabulary([])
        brains = catalog(portal_type=['Theme'])

        # Vocabulary term tokens *must* be 7 bit values, titles *must* be
        # unicode
        items = [SimpleTerm(brain.getPath(), b2a_qp(safe_encode(brain.UID)),
                            safe_unicode(brain.Title))
                 for brain in brains]
        return SimpleVocabulary(items)


class FacetedPortalTypesVocabulary(object):
    """Vocabulary factory for faceted portal types.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        ptool = getToolByName(context, 'plone_utils', None)
        ttool = getToolByName(context, 'portal_types', None)
        ftool = getToolByName(context, 'portal_faceted', None)

        if ptool is None or ttool is None:
            return SimpleVocabulary([])

        # items = dict((t, ttool[t].Title())
        #              for t in ptool.getUserFriendlyTypes())

        items = {
            'Advisory': u'Advisory',
            'MREvent': u'MREvent',
            'Study': u'Study',
            # 'DigiBib': u'DigiBib',
            'Hearing': u'Hearing',
            # 'Project': u'Project',
            # 'Theme': u'Theme',
            # 'Pressrelease': u'Pressrelease',
            # 'Folder': u'Folder',
            # 'Document': u'Page',
            # 'Meeting': u'Meeting',
            'AnnualReport': u'AnnualReport'
        }

        if ftool is not None:
            faceted_items = dict((t.getId(), t.title_or_id())
                                 for t in ftool.objectValues())
            items.update(faceted_items)

        items = items.items()
        items.sort(key=operator.itemgetter(1), cmp=compare)

        items = [SimpleTerm(i[0], i[0], i[1]) for i in items]
        return SimpleVocabulary(items)


ThemePathVocabularyFactory = ThemePathVocabulary()
FacetedPortalTypesVocabularyFactory = FacetedPortalTypesVocabulary()
