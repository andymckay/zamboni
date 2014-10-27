from nose.tools import eq_

import amo.tests
from mkt.api.models import Access
from mkt.site.fixtures import fixture
from mkt.users.models import UserProfile


class TestAPILockout(amo.tests.TestCase):
    fixtures = fixture('user_999')

    def setUp(self):
        self.user = UserProfile.objects.get(pk=999)
        self.access = Access.objects.create(user=self.user)

    def test_fail(self):
        self.access.has_failed()
        self.access.has_succeeded()
        eq_(self.access.failures, 1)
        eq_(self.access.is_locked_out(), False)

    def test_locked_out(self):
        with self.settings(MAX_API_LOGIN_FAILURES=1):
            self.access.has_failed()
            eq_(self.access.failures, 1)
            eq_(self.access.is_locked_out(), True)

    def test_succeed(self):
        with self.settings(MAX_API_LOGIN_FAILURES=1):
            self.access.has_failed()

        self.access.has_succeeded()
        eq_(self.access.is_locked_out(), False)

    def test_succeed_no_queries(self):
       with self.assertNumQueries(0):
            self.access.has_succeeded()
