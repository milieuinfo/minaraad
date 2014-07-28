# Connect to a mail server and send an email.  This is because there
# is no mailserver (or even a mail command) installed on the MMIS
# servers.
#
# Usage: echo "An error message from memmon" | python sendmail.py
#
# or even better, as memmon does:
#
# echo """To: m.van.rees@zestsoftware.nl
# Subject: Blah
#
# Hello.""" | python scripts/sendmail.py

import sys
import smtplib
from socket import gethostname

HOST = 'smtp-plone.mmis.be'
TO = 'm.van.rees@zestsoftware.nl, webadmin@zestsoftware.nl'
FROM = 'm.van.rees@zestsoftware.nl'
# The zestsoftware.nl domain uses SPF, which means the email gets
# bounced when trying to use a FROM address with that domain, because
# the mmis.be mail host is not in the SPF list for the zestsoftware.nl
# domain.  See http://www.openspf.org/Best_Practices/Webgenerated
SENDER = 'help@milieuinfo.be'

text = sys.stdin.read() + '\n\nSent from host: ' + gethostname()
info = {
    'to_address': TO,
    'from_address': FROM,
    'host': HOST,
    'text': text,
    }

conn = smtplib.SMTP(host=HOST)
# message = """To: %(to_address)s
# From: %(from_address)s
# Subject: Test mail

# %(text)s
# """
#
# Memmon only needs this:
message = """From: %(from_address)s
%(text)s
"""
if 'To: ' not in text:
    # Prepend To header.
    message = "To: %(to_address)s\n" + message
if ',' in TO:
    TO = [x.strip() for x in TO.split(',')]
else:
    TO = [TO]
conn.sendmail(SENDER, TO, message % info)
