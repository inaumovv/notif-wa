from datetime import timedelta, datetime, timezone
from decimal import Decimal

import requests
from celery import Celery, shared_task

import container
from config import settings
from helpers import DTOs
from main import logger

celery_app: Celery = Celery(
    'tasks',
    broker=f'{settings.REDIS_URL}/1',
    broker_connection_retry_on_startup=True,
    celery_broker_connection_retry=True,
    celery_result_backend=f'{settings.REDIS_URL}/1'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    worker_hijack_root_logger=False,
)

celery_app.autodiscover_tasks()


@shared_task(bind=True, default_retry_delay=5, max_retries=10)
def get_rents(self, status: int = 2, quantity: int = 100, dtos=DTOs, con=container):
    data: dict = {
        'results':
        [
            {
                'id': 1,
                'status_color': 'inrent',
                'client': {
                    'phone': '+79263540858',
                    'name': 'Игорь',
                },
                'rent_start': datetime(day=2, month=2, year=2025, tzinfo=timezone.utc),
                'rent_end': datetime(day=5, month=2, year=2025, hour=10, tzinfo=timezone.utc),
                'price_discount': 1500,
                'inventories': [
                    {
                        'id': 1,
                        'inventory_name': 'Молоток 1'
                    },
                    {
                        'id': 2,
                        'inventory_name': 'Отвертка 1'
                    },
                ],
                'time_exceed': False
            },
            {
                'id': 2,
                'status_color': 'inrent',
                'client': {
                    'phone': '+79263540858',
                    'name': 'Игорь',
                },
                'rent_start': datetime(day=2, month=2, year=2025, tzinfo=timezone.utc),
                'rent_end': datetime(day=5, month=2, year=2025, hour=17, tzinfo=timezone.utc),
                'price_discount': 1232,
                'inventories': [
                    {
                        'id': 3,
                        'inventory_name': 'Молоток 2'
                    },
                    {
                        'id': 4,
                        'inventory_name': 'Отвертка 2'
                    },
                ],
                'time_exceed': False
            }, {
                'id': 3,
                'status_color': 'completed',
                'client': {
                    'phone': '+79263540858',
                    'name': 'Игорь',
                },
                'rent_start': datetime(day=2, month=2, year=2025, tzinfo=timezone.utc),
                'rent_end': datetime(day=3, month=2, year=2025, hour=15, tzinfo=timezone.utc),
                'price_discount': 1232,
                'inventories': [
                    {
                        'id': 5,
                        'inventory_name': 'Молоток 3'
                    },
                    {
                        'id': 6,
                        'inventory_name': 'Отвертка 3'
                    },
                ],
                'time_exceed': False
            },

        ]
    }

    for entity in data['results']:
        notifications: bool | None = entity.get('notifications', None)
        if not notifications or notifications is True:
            rent_days: int = (entity['rent_end'] - entity['rent_start']).days
            day_price: Decimal = Decimal(entity['price_discount']/rent_days)
            rent_entity: dtos.RentEntity = dtos.RentEntity(
                id=entity['id'],
                status=dtos.Status[entity['status_color'].upper()],
                client=dtos.Client(phone=entity['client']['phone'], name=entity['client']['name']),
                rent_start=entity['rent_start'],
                rent_end=entity['rent_end'],
                price=Decimal(entity['price_discount']),
                day_price=day_price,
                inventories=[dtos.InventoryItem(id=item['id'], name=item['inventory_name']) for item in entity['inventories']],
                time_exceed=entity['time_exceed']

            )

            if rent_entity.status == dtos.Status.COMPLETED:
                con.case_manager.completed_rent(rent_entity)
            else:
                con.case_manager.new_case(rent_entity)


# @shared_task(bind=True, default_retry_delay=1, max_retries=10)
# def get_rents(self, status: int = 2, quantity: int = 100, dtos=DTOs, con=container):
#     logger.info(f'{status, quantity}')
#     try:
#         data: dict = con.api_client.get_rents(status, quantity)
#
#         for entity in data['results']:
#             notifications: bool | None = entity.get('notifications', None)
#             if not notifications or notifications is True:
#                 if entity['client']['phone'] == '+77088222869':
#                     rent_entity: dtos.RentEntity = dtos.RentEntity(
#                         id=entity['id'],
#                         status=dtos.Status[entity['status_color'].upper()],
#                         client=dtos.Client(phone=entity['client']['phone'], name=entity['client']['name']),
#                         rent_start=datetime.fromisoformat(entity['rent_start']).astimezone(tz=timezone.utc),
#                         rent_end=datetime.fromisoformat(entity['rent_end']).astimezone(tz=timezone.utc),
#                         price=Decimal(entity['price_discount']),
#                         inventories=[dtos.InventoryItem(name=item['inventory_name']) for item in entity['inventories']],
#                         time_exceed=entity['time_exceed']
#
#                     )
#
#                     if rent_entity.status == dtos.Status.COMPLETED:
#                         con.case_manager.completed_rent(rent_entity)
#                     else:
#                         con.case_manager.new_case(rent_entity)
#
#     except requests.HTTPError as err:
#         logger.error(err)
#         con.api_client.login()
#         raise self.retry(exc=err)
#
#     except Exception as e:
#         logger.error(e)


# @shared_task(bind=True, default_retry_delay=5, max_retries=10)
# def clean_redis(self, con=container):
#     try:
#         data: dict = con.api_client.get_rents(status=4)
#         for entity in data['results']:
#             con.redis.delete(entity['id'])
#
#     except requests.HTTPError as err:
#         logger.error(err)
#         con.api_client.login()
#         raise self.retry(exc=err)
#
#     except Exception as e:
#         logger.error(e)


celery_app.conf.beat_schedule = {
    'get-in-progress-rents': {
        'task': 'tasks.celery_app.get_rents',
        'schedule': timedelta(seconds=30)
    },
    # 'get-completed-rents': {
    #     'task': 'tasks.celery_app.get_rents',
    #     'schedule': timedelta(minutes=1, seconds=10),
    #     'kwargs': {
    #         'status': 4,
    #         'quantity': 100
    #     }
    # },
}
