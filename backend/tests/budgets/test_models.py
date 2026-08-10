"""
tests/budgets/test_models.py — Category model tests.
"""

import pytest
from django.db import IntegrityError
from django.db import transaction as db_transaction

from budgets.models import Category
from tests.factories import CategoryFactory

pytestmark = pytest.mark.django_db


class TestCategoryCreation:
    def test_creates_with_defaults(self, household):
        category = CategoryFactory(household=household, name='Groceries')
        assert category.id is not None
        assert category.type == Category.Type.SPENDING
        assert category.is_active is True
        assert category.household == household

    def test_creates_earning_category(self, household):
        category = CategoryFactory(household=household, name='Salary', type=Category.Type.EARNING)
        assert category.type == Category.Type.EARNING


class TestCategoryStr:
    def test_str_spending(self, household):
        category = CategoryFactory(
            household=household, name='Groceries', type=Category.Type.SPENDING
        )
        assert str(category) == 'Groceries (Spending)'

    def test_str_earning(self, household):
        category = CategoryFactory(household=household, name='Salary', type=Category.Type.EARNING)
        assert str(category) == 'Salary (Earning)'


class TestCategoryUniqueConstraint:
    def test_duplicate_household_name_type_raises(self, household):
        CategoryFactory(household=household, name='Groceries', type=Category.Type.SPENDING)
        with pytest.raises(IntegrityError):
            with db_transaction.atomic():
                CategoryFactory(household=household, name='Groceries', type=Category.Type.SPENDING)

    def test_same_name_different_type_allowed(self, household):
        """A household can have an 'Other' earning category and an 'Other'
        spending category at once — type is part of the category's identity,
        not a free-floating attribute of a name."""
        earning = CategoryFactory(household=household, name='Other', type=Category.Type.EARNING)
        spending = CategoryFactory(household=household, name='Other', type=Category.Type.SPENDING)
        assert earning.id != spending.id
        assert Category.objects.filter(household=household, name='Other').count() == 2

    def test_same_name_type_different_household_allowed(self, household, other_household):
        """The uniqueness constraint is scoped per household — two different
        households can each have their own 'Groceries' (spending) category."""
        CategoryFactory(household=household, name='Groceries', type=Category.Type.SPENDING)
        other = CategoryFactory(
            household=other_household, name='Groceries', type=Category.Type.SPENDING
        )
        assert other.id is not None

    def test_reactivating_soft_deleted_category_reuses_same_row(self, household):
        """Soft-delete never frees the (household, name, type) tuple — the API
        layer is expected to reactivate the existing row rather than create a
        new one. This test exercises that the row truly persists post-delete
        and can be flipped back on, sharing the same primary key."""
        category = CategoryFactory(
            household=household, name='Subscriptions', type=Category.Type.SPENDING
        )
        original_id = category.id

        category.is_active = False
        category.save()

        existing = Category.objects.filter(
            household=household, name='Subscriptions', type=Category.Type.SPENDING
        ).first()
        assert existing is not None
        assert existing.is_active is False

        existing.is_active = True
        existing.save()
        existing.refresh_from_db()

        assert existing.id == original_id
        assert (
            Category.objects.filter(
                household=household, name='Subscriptions', type=Category.Type.SPENDING
            ).count()
            == 1
        )


class TestCategoryCascadeDelete:
    def test_deleting_household_deletes_its_categories(self, household):
        CategoryFactory(household=household, name='Groceries')
        CategoryFactory(household=household, name='Salary', type=Category.Type.EARNING)
        household_id = household.id

        household.delete()

        assert Category.objects.filter(household_id=household_id).count() == 0

    def test_deleting_household_does_not_delete_other_households_categories(
        self, household, other_household
    ):
        CategoryFactory(household=household, name='Groceries')
        other_category = CategoryFactory(household=other_household, name='Rent')

        household.delete()

        assert Category.objects.filter(id=other_category.id).exists()
