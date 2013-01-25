from zope.component.hooks import getSite

from plone.app.users.browser.personalpreferences import UserDataPanelAdapter

from Products.minaraad.userdataschema import IEnhancedUserDataSchema


class EnhancedUserDataPanelAdapter(UserDataPanelAdapter):
    """ Adapter to store the extra fields in the memberdata.
    Note: there's black magic here.

    Basically:

     - in the __init__ we generate the properties based on the fields
       defined in IEnhancedUserDataSchema

     - we override __getattr__ so getters and setters for the fields are
       also there.
    """

    def __init__(self, *args, **kwargs):
        super(EnhancedUserDataPanelAdapter, self).__init__(*args, **kwargs)
        self.field_names  = [
            f.lower() for f in IEnhancedUserDataSchema._InterfaceClass__attrs.keys()]

        for field_name in self.field_names:
            if field_name in ('email', 'portrait', 'pdelete'):
                # These need special handling and they are handled
                # fine upstream in p.a.users already.
                continue
            setattr(EnhancedUserDataPanelAdapter,
                    field_name,
                    property(getattr(self, 'getp_%s' % field_name),
                             getattr(self, 'setp_%s' % field_name)))


    def __getattr__(self, name):
        # We first check we are calling get_/set_ on a known field.
        f_name = None
        if name.startswith('get_') or name.startswith('set_'):
            f_name = name[4:]

        elif name.startswith('getp_') or name.startswith('setp_'):
            f_name = name[5:]

        if f_name is None or f_name not in self.field_names:
            # Well, not one of the fields we manage.
            return UserDataPanelAdapter.__getattribute__(self, name)

        if name.startswith('get_'):
            def getter():
                return self._getProperty(f_name)

            return getter

        if name.startswith('set_'):
            def setter(value):
                if value is None:
                    value = ''
                    
                return self.context.setMemberProperties({f_name: value})
            return setter

        # These are more or less the same than the previous ones but are called when
        # using the property.
        # The main difference is that they take the instance as the first parameter.
        if name.startswith('getp_'):
            def pgetter(inst):
                return inst._getProperty(f_name)

            return pgetter

        if name.startswith('setp_'):
            def psetter(inst, value):
                if value is None:
                    value = ''
                    
                return inst.context.setMemberProperties({f_name: value})
            return psetter
