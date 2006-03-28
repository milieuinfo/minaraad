from zope import interface
from zope.interface.verify import verifyObject

from CipraSync.interfaces import ITransform, IDeferredTransform
from interfaces import IDontWrite

class DontWriteTransform:
    """A transformer for data that shouldn't be written.  See
    ``IDontWrite``.
    
    >>> t = DontWriteTransform()
    >>> value = t('something')
    >>> verifyObject(IDontWrite, value)
    True
    >>> value.value
    'something'
    """
    interface.implements(ITransform)

    class DontWrite:
        interface.implements(IDontWrite)
        value = None
        def __init__(self, value):
            self.value = value

    def __call__(self, data):
        return self.DontWrite(data)


class StreetAndHouseNumberTransform:
    """A transform from a string that contains street, housenumber and
    maybe bus information to a mapping of that contains the parsed
    values.

    >>> t = StreetAndHouseNumberTransform()
    >>> t("") # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    AttributeError: 'str' object has no attribute 'value'

    >>> DontWrite = DontWriteTransform.DontWrite

    >>> data = DontWrite('')
    >>> value = t(data)
    >>> verifyObject(IDontWrite, value)
    True
    >>> value = value.value
    >>> value['street'], value['housenumber'], value['bus']
    ('', '', '')
    >>> len(value)
    3

    >>> def printValues(string):
    ...     data = DontWrite(string)
    ...     value = t(data).value
    ...     print (value['street'], value['housenumber'], value['bus'])

    >>> printValues('Hoogstraat 42')
    ('Hoogstraat', '42', '')

    >>> printValues('Europees Parlement, Wiertzstraat ASP 11G205')
    ('Europees Parlement, Wiertzstraat ASP', '11G205', '')

    >>> printValues('Phoenix-gebouw - Koning Albert II-laan 19 bus 11')
    ('Phoenix-gebouw - Koning Albert II-laan', '19', '11')

    >>> printValues('Graaf de Ferraris-gebouw - '
    ...             'Koning Albert II-laan 20, bus 8')
    ('Graaf de Ferraris-gebouw - Koning Albert II-laan', '20', '8')
    """
    interface.implements(ITransform)

    def __call__(self, data):
        # Actual value is always contained in the ``value`` attribute
        # of the passed in data object:
        source = data.value
        value = {} # return value

        idx = 0
        for idx, char in enumerate(source):
            if ord(char) in range(ord('0'), ord('9')+1):
                break

        value['street'] = source[:idx].strip().strip('-,')

        busidx = source[idx:].lower().find('bus')
        if busidx == -1:
            busidx = len(source)
        else:
            busidx = busidx + idx

        value['housenumber'] = source[idx:busidx].strip().strip('-,')
        value['bus'] = source[busidx+3:].strip().strip('-,')

        data.value = value
        return data

class ZipCodeAndCityTransform:
    """A transform from a string that contains zipcode, city and maybe
    a ``ISO 3166-1 alpha-2`` country code.

    >>> t = ZipCodeAndCityTransform(default_country='BE')
    >>> t("") # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    AttributeError: 'str' object has no attribute 'value'

    >>> DontWrite = DontWriteTransform.DontWrite

    >>> data = DontWrite('')
    >>> value = t(data)
    >>> verifyObject(IDontWrite, value)
    True
    >>> value = value.value
    >>> value['zipcode'], value['city'], value['country']
    ('', '', '')
    >>> len(value)
    3
    
    >>> def printValues(string):
    ...     data = DontWrite(string)
    ...     value = t(data).value
    ...     print (value['country'], value['zipcode'], value['city'])

    >>> printValues('1000 Brussel')
    ('BE', '1000', 'Brussel')
    
    >>> printValues('9920     LOVENDEGEM')
    ('BE', '9920', 'Lovendegem')
    
    >>> printValues('NL-8000GB Zwolle')
    ('NL', '8000GB', 'Zwolle')

    >>> printValues('NL 8000 GB Zwolle wolle')
    ('NL', '8000GB', ' Zwolle Wolle')
    """
    interface.implements(ITransform)

    def __init__(self, default_country=''):
        self.default_country = default_country

    def __call__(self, data):
        # Actual value is always contained in the ``value`` attribute
        # of the passed in data object:
        source = data.value
        value = dict(country=self.default_country, zipcode='', city='')

        country_code = source[:2]
        if self._allUpperCase(country_code):
            # We have a country code at the beginning, which we want to
            # strip off.
            value['country'] = country_code
            source = source[3:]

        # We want to check if there is an extra two letter code behind
        # the zipcode that needs to be included.
        tokens = list(source.split())
        if len(tokens) != 0:
            value['zipcode'] = tokens[0]
            if len(tokens[1]) == 2 and self._allUpperCase(tokens[1]):
                value['zipcode'] += tokens[1]
                tokens[1] = ''

            city = ' '.join([token.capitalize() for token in tokens[1:]])
            value['city'] = city

        data.value = value
        return data

    def _allUpperCase(self, data):
        UPPERCASE = range(ord('A'), ord('Z') + 1)

        for char in data:
            if ord(char) not in UPPERCASE:
                return False

        return True


class FullNameTransform:
    """A deferred transform that uses the 'title' field to add to its
    value.

    >>> t = FullNameTransform()
    >>> t('van Huis', {})
    Traceback (most recent call last):
    ...
    KeyError: 'title'
    
    >>> t('van Huis', dict(title='Mr.'))
    'Mr. van Huis'
    """
    interface.implements(IDeferredTransform)

    def __call__(self, data, record):
        return '%s %s' % (record['title'], data)

def streetTransform(data, record):
    return record['streetandhousenumber'].value['street']
interface.directlyProvides(streetTransform, IDeferredTransform)

def housenumberTransform(data, record):
    return record['streetandhousenumber'].value['housenumber']
interface.directlyProvides(housenumberTransform, IDeferredTransform)

def busTransform(data, record):
    return record['streetandhousenumber'].value['bus']
interface.directlyProvides(busTransform, IDeferredTransform)

def zipcodeTransform(data, record):
    return record['zipcodeandcity'].value['zipcode']
interface.directlyProvides(zipcodeTransform, IDeferredTransform)

def cityTransform(data, record):
    return record['zipcodeandcity'].value['city']
interface.directlyProvides(cityTransform, IDeferredTransform)

def countryTransform(data, record):
    return record['zipcodeandcity'].value['country']
interface.directlyProvides(countryTransform, IDeferredTransform)
