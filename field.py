from Products.Archetypes import atapi

class OrderableReferenceWidget(atapi.ReferenceWidget):
    _properties = atapi.ReferenceWidget._properties.copy()
    _properties.update({
        'macro': 'orderablereference',
        'helper_js': ('orderablereference.js',),
        })
    

class OrderableReferenceField(atapi.ReferenceField):
    _properties = atapi.ReferenceField._properties.copy()
    _properties.update({
        'multiValued': True,
        'widget': OrderableReferenceWidget,
        })

    def set(self, instance, value, **kwargs):
        atapi.ReferenceField.set(self, instance, value, **kwargs)

        if value is None:
            value = ()

        if not isinstance(value, (list, dict)):
            value = value,

        #convert objects to uids if necessary
        uids = []
        for v in value:
            if isinstance(v, str):
                uids.append(v)
            else:
                uids.append(v.UID())

        refs = instance.getReferenceImpl(self.relationship)
        
        for ref in refs:
            index = uids.index(ref.targetUID)
            ref.order = index

    def get(self, instance, **kwargs):
        refs = instance.getReferenceImpl(self.relationship)
        refs.sort(lambda a,b:cmp(a.order, b.order))
        return refs
