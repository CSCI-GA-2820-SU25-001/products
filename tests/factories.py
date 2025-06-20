"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Product


class ProductFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Product

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("word")
    description = factory.Faker("sentence")
    price = factory.Faker("pyfloat", left_digits=3, right_digits=2, positive=True)
    available = True

    # Todo: Add your other attributes here...
