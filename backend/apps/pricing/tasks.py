from celery import shared_task

from apps.pricing.services.collector_services import CollectorService


@shared_task
def collect_prices():

    CollectorService.collect()

    return "Price collection completed!"