"""Import script for minaraad.

Usage: python start-import.py (html|members)
"""

import glob
import sys
from path import path

from tests.utils import setUpEnviron
setUpEnviron()

import zope.component
from CipraSync import interfaces
import minaraad.sync.configure

def usage():
    print __doc__
    sys.exit(1)

def html():
    minaraad.sync.configure.resolver()
    minaraad.sync.configure.transforms()
    minaraad.sync.configure.stupidreader()
    minaraad.sync.configure.writer()
    minaraad.sync.configure.writehandlers()
    urls = ('http://www.minaraad.be/tablad%202006.htm',
            'http://www.minaraad.be/tablad%202005.htm',
            'http://www.minaraad.be/tablad%202004.htm',
            'http://www.minaraad.be/tablad%202003.htm',
            'http://www.minaraad.be/tablad%202002.htm',
            'http://www.minaraad.be/tablad%202001.htm',
            'http://www.minaraad.be/tablad%202000.htm',
            
            'http://www.minaraad.be/nieuwsbrief/nieuwsbrief.htm',
            
            'http://www.minaraad.be/Persberichten/persberichten2003.htm')
    return urls


def members():
    minaraad.sync.configure.resolver()
    minaraad.sync.configure.transforms()
    minaraad.sync.configure.memberreader()
    minaraad.sync.configure.writer()
    minaraad.sync.configure.writehandlers()    
    input_dir = path(__file__).parent / 'input'
    return glob.glob(input_dir / '*')

def main():
    if len(sys.argv) != 2:
        usage()

    action = sys.argv[1]
    if action == 'html':
        names = html()
    elif action == 'members':
        names = members()
    else:
        usage()

    del sys.argv[1]
    
    print
    print "Starting the actual writing process..."


    reader = zope.component.getUtility(interfaces.IReader)
    reader.feed(names)
    writer = interfaces.IWriter(reader)
    writer.write()
    writer.commit()

    print
    print "Writing successful :)"
    print

if __name__ == '__main__':
    main()
