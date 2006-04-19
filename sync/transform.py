import locale
import time
import urllib2
import HTMLParser

from zope import interface
from zope.interface.verify import verifyObject

from CipraSync.interfaces import ITransform, IDeferredTransform
from interfaces import IDontWrite

from minaraad import BeautifulSoup
from Products.PortalTransforms.transforms import safe_html

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


def removeHTMLWhiteSpace(html):
    html = html.replace('&nbsp;', '')
    return ' '.join(html.split())

def fixEmail(string):
    charrefs = HTMLParser.charref.findall(string)
    if charrefs:
        email = ''.join([chr(int(ref[2:-1])) for ref in charrefs])
    else:
        email = string
    return email.strip()
    

def scrubHTML(html):
    valid = safe_html.VALID_TAGS.copy()
    wedontwant = ('span', 'p', 'br', 'sub', 'sup')
    for tag in wedontwant:
        del valid[tag]
    return safe_html.scrubHTML(html, valid=valid)

class SimpleRecord(dict):
    def __init__(self, category, **kwargs):
        self.category = category
        super(SimpleRecord, self).__init__(**kwargs)


class AdviezenScrapeTransform:
    """A transform that takes a URL and returns a list of records.

    >>> from pprint import pprint

    >>> transform = AdviezenScrapeTransform()
    >>> records = transform('http://www.minaraad.be/tablad%202003.htm')
    >>> len(records)
    74

    >>> pprint(records[0])
    {'date': (2003, 1, 16, 0, 0, 0, 3, 16, -1),
     'emails': ['francis.noyen@minaraad.be'],
     'files': ['http://www.minaraad.be/2003/2003-02.pdf'],
     'title': u'Vlarea &ndash; voorontwerp van besluit van de Vlaamse regering tot vaststelling van het Vlaams reglement inzake afvalvoorkoming en -beheer'}
    
    >>> pprint(records[-1])
    {'date': (2003, 12, 18, 0, 0, 0, 3, 352, -1),
     'emails': ['bea.kayaerts@minaraad.be'],
     'files': ['http://www.minaraad.be/adviesvragen/adviesvragen%202003/2003-75%20RL%20Meetjesland.pdf',
               'http://www.minaraad.be/2003/2003-75.pdf'],
     'title': u'Uitbreiding werkingsgebied regionaal landschap Meetjesland'}

    XXX more tests here

    Some HTML pages don't have a third column:

    >>> records = transform('http://www.minaraad.be/tablad%202000.htm')
    >>> len(records)
    31

    >>> pprint(records[0])
    {'date': (2000, 2, 10, 0, 0, 0, 3, 41, -1),
     'emails': [],
     'files': ['http://www.minaraad.be/2000/MiNa200006.pdf'],
     'title': u'Advies over het ontwerp van decreet houdende wijziging van het decreet van 18 mei 1999 houdende de organisatie van Ruimtelijke Ordening en van het decreet betreffende Ruimtelijke Ordening, geco\\xf6rdineerd op 22 oktober 1996'}
    >>> pprint(records[-1])
    {'date': (2000, 12, 7, 0, 0, 0, 3, 342, -1),
     'emails': [],
     'files': ['http://www.minaraad.be/2000/MiNa%20200038.pdf'],
     'title': u'Advies over de opdracht, functie en structuur van de MiNa-Raad'}
    
    Last but not least, 2002:

    >>> records = transform('http://www.minaraad.be/tablad%202002.htm')
    >>> len(records)
    51
    >>> pprint(records[22])
    {'date': (2002, 6, 26, 0, 0, 0, 2, 177, -1),
     'emails': ['dirk.uyttendaele@minaraad.be'],
     'files': ['http://www.minaraad.be/2002/2002-24.pdf'],
     'title': u'Advies over het kerntakendebat: Naar een kwaliteitsvolle organisatie van het bestuur op alle beleidsniveaus'}
    """
    interface.implements(ITransform)

    def __call__(self, url):
        records = []

        self.base = url[:url.rfind('/') + 1]

        locale.setlocale(locale.LC_ALL, 'nl_NL.utf8')

        html = urllib2.urlopen(url).read()
        html = html.replace('<center>', '').replace('</center>', '')
        html = scrubHTML(html)

        soup = BeautifulSoup.BeautifulSoup(html)

        year = soup.html.head.title.string.split()[1]

        # We need to fix up the content area, because some pages have
        # a number of tables:
        content = ''
        for table in soup('table')[5:-1]:
            stringified = ''.join([str(el) for el in table.contents])
            content += stringified
        content = BeautifulSoup.BeautifulSoup(content)
        
        for tr in content('tr'):
            records.extend(self._extractRecords(tr, year))

        locale.resetlocale()
        return records

    def _extractRecords(self, tr, year):
        # This corresponds to one <tr>
        records = []
        datetuple = self._extractDate(tr('td')[0], year)

        # the second <td> has title and e-mail, maybe multiple times
        titles, emails = self._extractTitlesAndEmails(tr('td')[1])

        # there can also be multiple pdfs, maybe in the second or
        # third td:
        filesTD = len(tr('td')) == 2 and tr('td')[1] or tr('td')[2]
        pdfs = self._extractFiles(filesTD)

        for idx in range(len(titles)):
            record = SimpleRecord('Advisory')
            record['date'] = datetuple
            record['title'] = titles[idx]
            record['emails'] = emails[idx]
            try:
                record['files'] = [pdfs[idx]]
            except IndexError:
                # XXX this is not a record
                continue
            records.append(record)

        if len(titles) == 1:
            # If we have only one title, we may have more than one PDF
            # belonging to it
            records[-1]['files'] = pdfs

        return records

    def _extractDate(self, td, year):
        datestr = td.string
        datestr = '%s %s' % (removeHTMLWhiteSpace(datestr), year)
        datetuple = time.strptime(datestr, '%d %B %Y')
        return datetuple

    def _extractTitlesAndEmails(self, td): # butt-ugly
        titles = []
        emails = []

        # This is for 1 record (one record may have mutltiple emails)
        title = ''
        emailz = []

        for el in td.contents:
            if (getattr(el, 'name', None) == 'a' and
                el['href'].startswith('mailto:')):
                emailz.append(fixEmail(el.string))
            else:
                string = removeHTMLWhiteSpace(el.string)
                if len(string) > 5: # We want to skip junk like '&' and 'en'
                    
                    # Have we already found a title?  If so, let's put
                    # the previously found title and e-mails into the
                    # record and move on with a new record:
                    if title:
                        titles.append(title)
                        emails.append(emailz)
                        title = ''
                        emailz = []

                    # Titles most often have a ' -' at the end which
                    # we want to get rid of
                    title = unicode(string, 'iso-8859-1')
                    if title[-2:] == u' -':
                        title = title[:-2]

        # We don't forget about the last ones
        titles.append(title)
        emails.append(emailz)
        return titles, emails

    def _extractFiles(self, td):
        return ['%s%s' % (self.base, el['href']) for el in td('a')]


class NieuwsbriefenScrapeTransform:
    """Another transform that takes a URL and returns a list of
    records.  This time it's Minaraad's Nieuwsbriefen page.

    >>> transform = NieuwsbriefenScrapeTransform()
    >>> records = transform(
    ...     'http://www.minaraad.be/nieuwsbrief/nieuwsbrief.htm')
    >>> len(records)
    31

    Let's print out the first 3 Nieuwsbrieven of 2003:

    >>> from pprint import pprint
    >>> twokthree = [r for r in records if r['title'].startswith('2003')]
    >>> pprint(twokthree[:3])
    [{'date': (2003, 3, 31, 0, 0, 0, 0, 90, -1),
      'files': ['http://www.minaraad.be/nieuwsbrief/nieuwsbrieven%202003/03-01%20Nieuwsbrief.pdf'],
      'title': '2003|01'},
     {'date': (2003, 4, 25, 0, 0, 0, 4, 115, -1),
      'files': ['http://www.minaraad.be/nieuwsbrief/nieuwsbrieven%202003/03-02%20Nieuwsbrief.pdf'],
      'title': '2003|02'},
     {'date': (2003, 5, 16, 0, 0, 0, 4, 136, -1),
      'files': ['http://www.minaraad.be/nieuwsbrief/nieuwsbrieven%202003/03-03%20Nieuwsbrief.pdf'],
      'title': '2003|03'}]
    """
    interface.implements(ITransform)

    def __call__(self, url):
        records = []

        self.base = url[:url.rfind('/') + 1]

        locale.setlocale(locale.LC_ALL, 'nl_NL.utf8')

        html = urllib2.urlopen(url).read()
        html = html.replace('<center>', '').replace('</center>', '')
        html = scrubHTML(html)

        soup = BeautifulSoup.BeautifulSoup(html)

        links = soup.fetch('a', {'href': lambda s:s and s.endswith('pdf')})
        for link in links:
            record = SimpleRecord('File')
            record['date'] = self._makeDate(link.string)
            record['title'] = removeHTMLWhiteSpace(link.string)
            record['files'] = [link['href'].startswith('http://') and
                               link['href'] or self.base + link['href']]
            records.append(record)
        
        locale.resetlocale()
        return records

    def _makeDate(self, link):
        # Health warning: very silly code ahead
        def ttuple(string):
            try:
                return time.strptime(string, '%d %B %Y')
            except ValueError:
                return None
        
        node = link.next.next
        while True:
            string = removeHTMLWhiteSpace(node.string)
            if string:
                if ttuple(string):
                    return ttuple(string)
                
                # in one case, the string is only month and year,
                # and the previous node holds the day:
                day = node.previous.string[-2:]
                string = ' '.join((day, string))
                if ttuple(string):
                    return ttuple(string)

                # in yet another case the date is somewhere else completely:
                daymonth = removeHTMLWhiteSpace(link.next.string.split('-')[1])
                year = removeHTMLWhiteSpace(node.string)
                string = ' '.join((daymonth, year))
                if ttuple(string):
                    return ttuple(string)
            else:
                node = node.next
        

class PersberichtenScrapeTransform:
    """Another transform that takes a URL and returns a list of
    records.  This time it's Minaraad's Persberichten page.

    >>> transform = PersberichtenScrapeTransform()
    >>> records = transform(
    ...     'http://www.minaraad.be/Persberichten/persberichten2003.htm')
    >>> len(records)
    53
    >>> records[0]['date'], records[0]['title']
    ((2006, 2, 3, 0, 0, 0, 4, 34, -1), 'Uitvoering RSV')
    >>> records[-1]['date'], records[-1]['title']
    ((2005, 12, 1, 0, 0, 0, 3, 335, -1), 'Slimme kilometerheffing')
    >>> records[-1]['files'] # doctest: +ELLIPSIS
    ['http://www.minaraad.be/Persberichten/persberichten%202005/persbericht%20van%2001%20december%202005.pdf']
    """
    interface.implements(ITransform)

    def __call__(self, url):
        records = []

        self.base = url[:url.rfind('/') + 1]

        locale.setlocale(locale.LC_ALL, 'nl_NL.utf8')

        html = urllib2.urlopen(url).read()
        html = html.replace('<center>', '').replace('</center>', '')
        html = scrubHTML(html)

        soup = BeautifulSoup.BeautifulSoup(html)

        links = soup.fetch('a', {'href': lambda s:s and s.endswith('pdf')})
        for link in links:
            record = SimpleRecord('Pressrelease')
            record['date'] = self._makeDate(link.string)
            record['title'] = self._extractTitle(link)
            record['files'] = [self.base + link['href']]
            records.append(record)
        
        locale.resetlocale()
        return records

    def _extractTitle(self, link):
        node = link.next.next
        while True:
            string = removeHTMLWhiteSpace(node.string)
            if string:
                return string
            else:
                node = node.next

    def _makeDate(self, string):
        return time.strptime(removeHTMLWhiteSpace(string), '%d %B %Y')
        
