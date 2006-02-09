## Controlled Python Script "validate_prefs_minaraad"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##title=Checks for existence of properties of Minaraad
##

def missing(field):
    state.setError(field, 'You must enter a value.', 'missing_%s' % field)


request = context.REQUEST
for field in ('fullname', 'street','housenumber', 'zipcode', 'city'):
    if not request.get(field):
        missing(field)

if state.getErrors():
    return state.set(
        status='failure',
        portal_status_message='Please correct the indicated errors.')
else:
    return state

