'''\
Migration reindex catalog patch

During the migration, the catalog reindex must keep a *really* low
threshhold. This makes sure the results are committed into a subtransaction
ever often. If this is not ensured, reindexing will go to quasi
infinite memory consumption.

Possible candidate that triggers this is pdf files.
'''

from Products.CMFCore.utils import getToolByName
import logging
logger = logging.getLogger('Minaraad_monkey')

def _reindexCatalog(portal, out):
    """Rebuilds the portal_catalog."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        # Reduce threshold for the reindex run
        old_threshold = catalog.threshold
        pg_threshold = getattr(catalog, 'pgthreshold', 0)
        catalog.pgthreshold = 300
        catalog.threshold = 20  # XXX Must be kept so low!
        catalog.refreshCatalog(clear=1)
        catalog.threshold = old_threshold
        catalog.pgthreshold = pg_threshold
        out.append("Reindexed portal_catalog.")

# Do the monkey patch
import Products.CMFPlone.migrations
Products.CMFPlone.migrations.v2_1.alphas.reindexCatalog = _reindexCatalog
Products.CMFPlone.migrations.v2_1.two12_two13.reindexCatalog = _reindexCatalog
Products.CMFPlone.migrations.v2_1.betas.reindexCatalog = _reindexCatalog
Products.CMFPlone.migrations.v2_1.rcs.reindexCatalog = _reindexCatalog
Products.CMFPlone.migrations.v2_5.final_two51.reindexCatalog = _reindexCatalog
Products.CMFPlone.migrations.v2_5.betas.reindexCatalog = _reindexCatalog
logger.info('*** migration_reindex_catalog patch applied ***')
