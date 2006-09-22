import zope.component
from path import path

import CipraSync.write

import minaraad.sync.read
import minaraad.sync.write
import minaraad.sync.transform


# resolvers
def resolver():
    zope.component.provideUtility(
        minaraad.sync.write.MinaResolver('/minaraad'),
        name='mina-resolver')


# transforms
def transforms():
    zope.component.provideUtility(
        minaraad.sync.transform.DontWriteTransform(),
        name='mina-transform-dontwrite',
        )

    zope.component.provideUtility(
        minaraad.sync.transform.StreetAndHouseNumberTransform(),
        name='mina-transform-streetandhousenumber',
        )

    zope.component.provideUtility(
        minaraad.sync.transform.ZipCodeAndCityTransform(
        default_country='Belgie'),
        name='mina-transform-zipcodeandcity',
        )

    zope.component.provideUtility(
        minaraad.sync.transform.streetTransform,
        name='mina-transform-street',
        )

    zope.component.provideUtility(
        minaraad.sync.transform.housenumberTransform,
        name='mina-transform-housenumber',
        )
    
    zope.component.provideUtility(
        minaraad.sync.transform.busTransform,
        name='mina-transform-bus',
        )
    
    zope.component.provideUtility(
        minaraad.sync.transform.zipcodeTransform,
        name='mina-transform-zipcode',
        )
    
    zope.component.provideUtility(
        minaraad.sync.transform.cityTransform,
        name='mina-transform-city',
        )
    
    zope.component.provideUtility(
        minaraad.sync.transform.countryTransform,
        name='mina-transform-country',
        )
    

    zope.component.provideUtility(
        minaraad.sync.transform.AdviezenScrapeTransform(),
        name='mina-transform-adviezenscrape',
        )
    
    zope.component.provideUtility(
        minaraad.sync.transform.NieuwsbrievenScrapeTransform(),
        name='mina-transform-nieuwsbrievenscrape',
        )
    
    zope.component.provideUtility(
        minaraad.sync.transform.PersberichtenScrapeTransform(),
        name='mina-transform-persberichtenscrape',
        )
    

# Our two readers
def memberreader():
    configuration = path(__file__).parent / 'etc' / 'memberreader.ini'
    zope.component.provideUtility(
        minaraad.sync.read.MemberReader(configuration=configuration))
    
def stupidreader():
    configuration = path(__file__).parent / 'etc' / 'stupidreader.ini'
    zope.component.provideUtility(
        minaraad.sync.read.StupidTransformReader(configuration=configuration))
    
# writer and writehandlers
def writer():
    Writer = CipraSync.write.Writer
    Writer.configuration = path(__file__).parent / 'etc' / 'writer.ini'
    zope.component.provideAdapter(CipraSync.write.Writer)

def writehandlers():
    zope.component.provideAdapter(
        minaraad.sync.write.MemberPropertyHandler,
        name='mina-memberpropertyhandler')

    zope.component.provideAdapter(
        minaraad.sync.write.AdviezenScrapeHandler,
        name='mina-adviezenscrapehandler')
    zope.component.provideAdapter(
        minaraad.sync.write.NieuwsbriefScrapeHandler,
        name='mina-nieuwsbriefscrapehandler')
    zope.component.provideAdapter(
        minaraad.sync.write.PersberichtenScrapeHandler,
        name='mina-persberichtenscrapehandler')
