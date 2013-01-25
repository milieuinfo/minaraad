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

HOST = 'smtp-plone.mmis.be'
TO = 'm.van.rees@zestsoftware.nl'
FROM = 'm.van.rees@zestsoftware.nl'

text = sys.stdin.read()
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
conn.sendmail(FROM, [TO], message % info)