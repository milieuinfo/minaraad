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
    >>> value = t("")
    >>> value['street'], value['housenumber'], value['bus']
    ('', '', '')
    >>> len(value)
    3

    >>> def printValues(string):
    ...     value = t(string)
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
        value = {} # return value

        idx = 0
        for idx, char in enumerate(data):
            if ord(char) in range(ord('0'), ord('9')+1):
                break

        value['street'] = data[:idx].strip().strip('-,')

        busidx = data[idx:].lower().find('bus')
        if busidx == -1:
            busidx = len(data)
        else:
            busidx = busidx + idx

        value['housenumber'] = data[idx:busidx].strip().strip('-,')
        value['bus'] = data[busidx+3:].strip().strip('-,')

        return value

class ZipCodeAndCityTransform:
    """A transform from a string that contains zipcode, city and maybe
    a ``ISO 3166-1 alpha-2`` country code.

    >>> t = ZipCodeAndCityTransform(default_country='Belgie')
    >>> value = t("")
    >>> value['zipcode'], value['city'], value['country']
    ('', '', '')
    >>> len(value)
    3
    
    >>> def printValues(string):
    ...     value = t(string)
    ...     print (value['country'], value['zipcode'], value['city'])

    >>> printValues('1000 Brussel')
    ('Belgie', '1000', 'Brussel')
    
    >>> printValues('9920     LOVENDEGEM')
    ('Belgie', '9920', 'Lovendegem')
    
    >>> printValues('NL-8000GB Zwolle')
    ('Nederland', '8000GB', 'Zwolle')

    >>> printValues('NL 8000 GB Zwolle wolle')
    ('Nederland', '8000GB', ' Zwolle Wolle')
    """
    interface.implements(ITransform)

    country_map = {
        'BE': 'Belgie',
        'NL': 'Nederland',
        }

    def __init__(self, default_country=''):
        self.default_country = default_country

    def __call__(self, data):
        value = dict(country=self.default_country, zipcode='', city='')

        country_code = data[:2]
        if self._allUpperCase(country_code):
            # We have a country code at the beginning, which we want to
            # strip off.
            value['country'] = self.country_map.get(country_code,
                                                    country_code)
            data = data[3:]

        # We want to check if there is an extra two letter code behind
        # the zipcode that needs to be included.
        tokens = list(data.split())
        if len(tokens) != 0:
            value['zipcode'] = tokens[0]
        if len(tokens) > 1:
            if len(tokens[1]) == 2 and self._allUpperCase(tokens[1]):
                value['zipcode'] += tokens[1]
                tokens[1] = ''

            city = ' '.join([token.capitalize() for token in tokens[1:]])
            value['city'] = city

        return value

    def _allUpperCase(self, data):
        UPPERCASE = range(ord('A'), ord('Z') + 1)

        for char in data:
            if ord(char) not in UPPERCASE:
                return False

        return True

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


