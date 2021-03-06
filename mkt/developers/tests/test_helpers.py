# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils import translation

from mock import Mock
from nose.tools import eq_
from pyquery import PyQuery as pq

import amo
import amo.tests
from amo.tests.test_helpers import render
from mkt.developers import helpers
from mkt.users.models import UserProfile


def test_hub_page_title():
    translation.activate('en-US')
    request = Mock()
    addon = Mock()
    addon.name = 'name'
    ctx = {'request': request, 'addon': addon}

    title = 'Oh hai!'
    s1 = render('{{ hub_page_title("%s") }}' % title, ctx)
    s2 = render('{{ page_title("%s | Developers") }}' % title, ctx)
    eq_(s1, s2)

    s1 = render('{{ hub_page_title() }}', ctx)
    s2 = render('{{ page_title("Developers") }}', ctx)
    eq_(s1, s2)

    s1 = render('{{ hub_page_title("%s", addon) }}' % title, ctx)
    s2 = render('{{ page_title("%s | %s") }}' % (title, addon.name), ctx)
    eq_(s1, s2)


class TestDevBreadcrumbs(amo.tests.TestCase):

    def setUp(self):
        self.request = Mock()

    def test_no_args(self):
        s = render('{{ hub_breadcrumbs() }}', {'request': self.request})
        eq_(s, '')

    def test_with_items(self):
        s = render("""{{ hub_breadcrumbs(items=[('/foo', 'foo'),
                                                ('/bar', 'bar')]) }}'""",
                  {'request': self.request})
        crumbs = pq(s)('li')
        expected = [
            ('Home', reverse('home')),
            ('Developers', reverse('ecosystem.landing')),
            ('foo', '/foo'),
            ('bar', '/bar'),
        ]
        amo.tests.check_links(expected, crumbs, verify=False)

    def test_with_app(self):
        product = Mock()
        product.name = 'Steamcube'
        product.id = 9999
        product.app_slug = 'scube'
        product.type = amo.ADDON_WEBAPP
        s = render("""{{ hub_breadcrumbs(product) }}""",
                   {'request': self.request, 'product': product})
        crumbs = pq(s)('li')
        expected = [
            ('Home', reverse('home')),
            ('Developers', reverse('ecosystem.landing')),
            ('My Submissions', reverse('mkt.developers.apps')),
            ('Steamcube', None),
        ]
        amo.tests.check_links(expected, crumbs, verify=False)

    def test_with_app_and_items(self):
        product = Mock()
        product.name = 'Steamcube'
        product.id = 9999
        product.app_slug = 'scube'
        product.type = amo.ADDON_WEBAPP
        product.get_dev_url.return_value = reverse('mkt.developers.apps.edit',
                                                 args=[product.app_slug])
        s = render("""{{ hub_breadcrumbs(product,
                                         items=[('/foo', 'foo'),
                                                ('/bar', 'bar')]) }}""",
                   {'request': self.request, 'product': product})
        crumbs = pq(s)('li')
        expected = [
            ('Home', reverse('home')),
            ('Developers', reverse('ecosystem.landing')),
            ('My Submissions', reverse('mkt.developers.apps')),
            ('Steamcube', product.get_dev_url()),
            ('foo', '/foo'),
            ('bar', '/bar'),
        ]
        amo.tests.check_links(expected, crumbs, verify=False)


def test_log_action_class():
    v = Mock()
    for k, v in amo.LOG_BY_ID.iteritems():
        if v.action_class is not None:
            cls = 'action-' + v.action_class
        else:
            cls = ''
        eq_(render('{{ log_action_class(id) }}', {'id': v.id}), cls)


class TestDevAgreement(amo.tests.TestCase):

    def setUp(self):
        self.user = UserProfile()

    def test_none(self):
        with self.settings(DEV_AGREEMENT_LAST_UPDATED=None):
            eq_(helpers.dev_agreement_ok(self.user), True)

    def test_date_oops(self):
        with self.settings(DEV_AGREEMENT_LAST_UPDATED=('wat?')):
            eq_(helpers.dev_agreement_ok(self.user), True)

    def test_not_agreed(self):
        # The user has never agreed to it so in this case we don't need to
        # worry them about changes.
        self.user.update(read_dev_agreement=None)
        with self.settings(DEV_AGREEMENT_LAST_UPDATED=
                           self.days_ago(10).date()):
            eq_(helpers.dev_agreement_ok(self.user), True)

    def test_past_agreed(self):
        self.user.update(read_dev_agreement=self.days_ago(10))
        with self.settings(DEV_AGREEMENT_LAST_UPDATED=self.days_ago(5).date()):
            eq_(helpers.dev_agreement_ok(self.user), False)

    def test_not_past(self):
        self.user.update(read_dev_agreement=self.days_ago(5))
        with self.settings(DEV_AGREEMENT_LAST_UPDATED=
                           self.days_ago(10).date()):
            eq_(helpers.dev_agreement_ok(self.user), True)
