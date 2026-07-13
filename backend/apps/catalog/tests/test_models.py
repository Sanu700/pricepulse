import pytest
from apps.catalog.models import Category


@pytest.mark.django_db
def test_create_category():
    category = Category.objects.create(name="Beverages")

    assert category.name == "Beverages"
    assert Category.objects.count() == 1