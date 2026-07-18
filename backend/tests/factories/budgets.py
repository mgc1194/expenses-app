"""
tests/factories/budgets.py — factory_boy factories for the budgets app.
"""

import factory

from budgets.models import Category


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'Category {n}')
    type = Category.Type.SPENDING
    is_active = True
    household = factory.SubFactory('tests.factories.HouseholdFactory')
