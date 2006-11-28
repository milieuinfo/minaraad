##parameters=

# Fix TXNG indexes.
# XXX before running this script, make sure you have TXNG3 3.1.13 or higher
# installed.

encoding = context.portal_properties.site_properties.default_charset

metatypes =  ['ZCTextIndex', 'TextIndex', 'TextIndexNG2', 'TextIndexNG3']

catalog = context.portal_catalog
indexes = catalog.getIndexObjects()
existing_ids = [idx.getId() for idx in indexes if idx.meta_type in metatypes]
all_ids = list(existing_ids)
needed = ('SearchableText', 'Title', 'Description')
for id in needed:
    if not id in all_ids:
        all_ids.append(id)

for id in all_ids:

    if id in existing_ids:
        catalog.manage_delIndex(id)
    catalog.manage_addIndex(id, 'TextIndexNG3', extra={'languages': ('en', 'nl'), # XXX adjust your languages as desired
                                                           'default_encoding' : encoding,
                                                           'splitter_casefolding' : True,
                                                           'dedicated_storages' : True,
                                                           'use_converters' : True,
                                                           'index_unknown_languages' : True,
                                                           'storage' : 'txng.storages.term_frequencies',
                                                           'ranking' : True,
                                                           })

# Reduce threshold for the reindex run
# If left on the original, it bloats memory above 2G and onward.
# Probably, because of pdf or msw content indexing?
# XXX this is a speciality of the Minaraad site and should
# XXX not be applied with other sites, because it slows down indexing
# XXX on behalf of a smaller memory footprint
old_threshold = catalog.threshold
pg_threshold = getattr(catalog, 'pgthreshold', 0)
catalog.manage_setProgress(300)
catalog.manage_edit(context.REQUEST.RESPONSE, '', min(20, old_threshold))  # XXX Must be kept so low!

# do the reindexing
catalog.manage_reindexIndex(all_ids, context.REQUEST)

# resume original thresholds
catalog.manage_setProgress(old_threshold)
catalog.manage_edit(context.REQUEST.RESPONSE, '', pg_threshold)

context.REQUEST.RESPONSE.redirect('txng_maintenance?portal_status_message=All+TXNG+indexes+fixed+for+Minaraad')    
