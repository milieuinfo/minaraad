import glob
from path import path

import zope.component

from tests.utils import setUpEnviron
setUpEnviron()

from CipraSync import interfaces
import minaraad.sync.configure

def main():
    print
    print "Starting the actual writing process..."

    minaraad.sync.configure.resolver()
    minaraad.sync.configure.transforms()
    minaraad.sync.configure.memberreader()
    minaraad.sync.configure.writer()
    minaraad.sync.configure.writehandlers()    

    reader = zope.component.getUtility(interfaces.IReader)
    input_dir = path(__file__).parent / 'input'
    reader.feed(glob.glob(input_dir / '*'))
    writer = interfaces.IWriter(reader)
    writer.write()
    writer.commit()

    print
    print "Writing successful :)"
    print

if __name__ == '__main__':
    main()
