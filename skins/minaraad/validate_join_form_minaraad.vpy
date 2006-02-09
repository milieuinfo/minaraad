## Controller Python Script "validate_join_form_minaraad"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=validates the Registration of a User

def missing(field):
    state.setError(
        field,
        "This field is required, please provide some information.",
        'input_required')

request = context.REQUEST

required_fields = ('fullname', 'street', 'housenumber', 'zipcode', 'city')
for field in required_fields:
    if not request.get(field):
        missing(field)

if state.getErrors():
    return state.set(
        status='failure',
        portal_status_message='Please correct the indicated errors.')
else:
    return state
