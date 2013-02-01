#! /bin/sh
i18ndude rebuild-pot --pot locales/minaraad.pot --create minaraad \
    --merge locales/manual.pot .

for po in locales/*/LC_MESSAGES/minaraad.po; do
    i18ndude sync --pot locales/minaraad.pot $po
done

i18ndude rebuild-pot --pot locales/plone.pot --merge locales/plone-manual.pot --create plone profiles
for po in locales/*/LC_MESSAGES/plone.po; do
    i18ndude sync --pot locales/plone.pot $po
done

#echo "Reporting some statistics..."
# Find places that are missing an "i18n:translate" or
# "i18n:attributes" tag.
#i18ndude find-untranslated -s $TEMPLATE_FILES

#echo "Percentage done per language:"
#i18ndude chart -o /dev/null --pot i18n/$PROJECT.pot i18n/$PROJECT-*.po
