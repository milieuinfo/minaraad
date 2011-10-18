## Controller Python Script "validate_join_form_minaraad"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=validates the Registration of a User

from Products.CMFPlone import PloneMessageFactory as PMF

def missing(field):
    state.setError(
        field,
        PMF("This field is required, please provide some information."),
        'input_required')

request = context.REQUEST

required_fields = ('firstname','fullname', 'street', 'housenumber', 'zipcode', 'city')
for field in required_fields:
    if not request.get(field):
        missing(field)

if not context.restrictedTraverse('@@captcha').verify():
    state.setError(
        'captcha',
        "Captcha validation failed. Please try again.")

if state.getErrors():
    return state.set(
        status='failure',
        portal_status_message='Please correct the indicated errors.')
else:
    return state
