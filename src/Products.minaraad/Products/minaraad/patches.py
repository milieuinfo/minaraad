import os, urllib, urllib2
from recaptcha.client import captcha

def submit(*args, **kwargs):
    """
    Patch for recaptcha.client.captcha.submit to handle http proxy.
    """
    if 'http_proxy' in os.environ:
        proxy_support = urllib2.ProxyHandler()
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)
    return captcha.old_submit(*args, **kwargs)


def patch_captcha():
    captcha.old_submit = captcha.submit
    captcha.submit = submit

def unpatch_captcha():
    captcha.submit = captcha.old_submit


def patch_all():
    patch_captcha()

def unpatch_all():
    unpatch_captcha()
