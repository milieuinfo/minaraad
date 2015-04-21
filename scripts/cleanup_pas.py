"""Cleanup Pluggable Authentication Service (PAS).

Roles in Portal role manager can have assigned principals that no longer exist.

Same for groups.

Same for memberdata.

Clean this up.

"""

# Run this with:
# bin/instance run scripts/cleanup_pas.py
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import setSite
import transaction

# Get all Plone Sites.
# app is the Zope root.
plones = [obj for obj in app.objectValues()
          if getattr(obj, 'portal_type', '') == 'Plone Site']

for site in plones:
    print('')
    print('Handling Plone Site %s.' % site.id)
    setSite(site)
    pas = getToolByName(site, 'acl_users')

    # Roles
    roleman = pas.portal_role_manager
    to_delete = []
    for principal_id, role_ids in roleman._principal_roles.items():
        info = pas.searchPrincipals(id=principal_id, exact_match=True)
        if len(info) == 0:
            # Gather list for handling after we have gone through
            # all items.
            to_delete.append((principal_id, role_ids))
    for principal_id, role_ids in to_delete:
        print("Removing non-existing principal %r from roles %r" % (
            principal_id, role_ids))
        for role_id in role_ids:
            try:
                roleman.removeRoleFromPrincipal(role_id, principal_id)
            except KeyError:
                print("Warning: could not remove principal %r from role %r" % (
                    principal_id, role_id))
        # Remove the key, otherwise you keep an empty list.
        del roleman._principal_roles[principal_id]
    print("Removed %d non-existing principals from roles." % len(to_delete))

    note = 'Cleaned PAS for Plone Site %s.' % site.id
    print(note)
    # Commit transaction and add note.
    tr = transaction.get()
    tr.note(note)
    transaction.commit()
print('Done.')
