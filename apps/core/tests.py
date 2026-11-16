from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse


def make_user(name, group=None):
    user = User.objects.create_user(name, password="x")
    if group:
        user.groups.add(Group.objects.get(name=group))
    return user


class RoleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles")
        cls.audit = make_user("audit", "IT Audit")
        cls.clerk = make_user("clerk", "User")
        cls.manager = make_user("manager", "Administrator")
        cls.nobody = make_user("nobody")

    def code(self, user, url_name):
        self.client.force_login(user)
        return self.client.get(reverse(url_name)).status_code

    def test_anonymous_goes_to_login(self):
        self.assertEqual(self.client.get(reverse("asset_list")).status_code, 302)

    def test_audit_views_but_cannot_create(self):
        self.assertEqual(self.code(self.audit, "asset_list"), 200)
        self.assertEqual(self.code(self.audit, "asset_create"), 403)

    def test_user_and_admin_can_create(self):
        self.assertEqual(self.code(self.clerk, "asset_create"), 200)
        self.assertEqual(self.code(self.manager, "asset_create"), 200)

    def test_no_role_sees_nothing(self):
        self.assertEqual(self.code(self.nobody, "asset_list"), 403)
