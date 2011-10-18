#!/bin/sh
I18NDOMAIN='minaraad.projects'

# Synchronise the .pot with the templates.
#i18ndude rebuild-pot --pot locales/${I18NDOMAIN}.pot --merge locales/${I18NDOMAIN}-manual.pot --create ${I18NDOMAIN} .
i18ndude rebuild-pot --pot locales/${I18NDOMAIN}.pot --create ${I18NDOMAIN} .

# Synchronise the resulting .pot with the .po files
i18ndude sync --pot locales/${I18NDOMAIN}.pot locales/en/LC_MESSAGES/${I18NDOMAIN}.po
i18ndude sync --pot locales/${I18NDOMAIN}.pot locales/nl/LC_MESSAGES/${I18NDOMAIN}.po

# Do the plone domain as well, at least for stuff in the profiles. The
# rest is probably not needed, or we would get far too much in here
# that is already translated elsewhere, just because we copied a
# template for a one line change.
i18ndude rebuild-pot --pot i18n/plone.pot --merge i18n/manual.pot --create plone profiles/
i18ndude sync --pot i18n/plone.pot i18n/plone-minaraad.projects-nl.po 
