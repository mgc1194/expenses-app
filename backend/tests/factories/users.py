"""
tests/factories/users.py — Factories for Household and CustomUser.
"""

import factory

from users.models import CustomUser, Household


class HouseholdFactory(factory.django.DjangoModelFactory):
    """Creates a Household with a unique generated name."""

    class Meta:
        model = Household

    name = factory.Sequence(lambda n: f'Household {n}')


class UserFactory(factory.django.DjangoModelFactory):
    """
    Creates a CustomUser with a sequenced username/email and a fixed password.

    The user is NOT added to any household by default.  Add via:
        user = UserFactory()
        user.households.add(household)

    Or use the convenience helper:
        household = HouseholdFactory()
        user = UserFactory(households=[household])   # via post_generation
    """

    class Meta:
        model = CustomUser
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'Password1!')

    @factory.post_generation
    def households(self, create, extracted, **kwargs):
        """Optionally add the user to one or more households on creation.

        Usage:
            UserFactory(households=[my_household])
        """
        if not create or not extracted:
            return
        for household in extracted:
            self.households.add(household)
