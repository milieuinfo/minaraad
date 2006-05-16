from StringIO import StringIO
from Products.CMFCore.utils import getToolByName

def buildCSV(context, members, filename='members.csv'):
    portalProperties = getToolByName(context, 'portal_properties')
    siteProperties = portalProperties.site_properties
    charset = siteProperties.getProperty('default_charset')
    
    out = StringIO()
    
    fields = (('gender', 'Aanhef'), 
              ('firstname', 'Voornaam'),
              ('fullname', 'Achternaam'),
              ('company', 'Organisatie'),
              ('jobtitle', 'Functie'),
              ('street', 'Straat'),
              ('housenumber', 'Huisnummer'),
              ('bus', 'Bus'),
              ('zipcode', 'Postcode'),
              ('city', 'Woonplaats'),
              ('country', 'Land'),
              ('other_country', 'Ander land'),
              ('phonenumber', 'Telefoonnummer'),
              ('email', 'E-mail'))
        
    for pos, field in enumerate(fields):
        id, title = field
            
        out.write(u'"%s"' % title)
        if pos < len(fields)-1:
            out.write(u',')
            
    out.write(u'\n')

    for member in members:
        for pos, field in enumerate(fields):
            id, title = field
            value = unicode(getattr(member, id, ''), charset)
            value = value.replace(u'"', u'""')
            out.write(u'"%s"' % value)
        
            if pos < len(fields)-1:
                out.write(u',')

        out.write(u'\n')

    response = context.REQUEST.RESPONSE
    response.setHeader('content-type',
                       'application/vnd.ms-excel; charset=%s' % charset)
    response.setHeader('content-disposition',
                       'attachment; filename=%s' % filename)
    
    return out.getvalue().encode('iso-8859-1')
    
