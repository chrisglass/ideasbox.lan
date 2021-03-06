from django.conf import settings

import factory

from ..models import Document


class DocumentFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: "Test document {0}".format(n))
    summary = "This is a test summary"
    lang = settings.LANGUAGE_CODE
    original = factory.django.FileField()
    credits = "Document credits"

    class Meta:
        model = Document
