from django.core.management.base import BaseCommand

from apps.pricing.services.collector_services import CollectorService


class Command(BaseCommand):

    help = "Collect latest prices"

    def handle(self, *args, **kwargs):

        CollectorService.collect()

        self.stdout.write(
            self.style.SUCCESS(
                "Price collection completed successfully!"
            )
        )