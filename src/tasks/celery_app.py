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


@shared_task(bind=True, default_retry_delay=1, max_retries=10)
def get_rents(self, status: int = 2, quantity: int = 100, dtos=DTOs, con=container):
    logger.info(f'{status, quantity}')
    try:
        data: dict = con.api_client.get_rents(status, quantity)
        logger.info(f'Сделали успешный запрос')

        for entity in data['results']:
            notifications: bool | None = entity.get('notifications', None)
            if not notifications or notifications is True:
                if entity['client']['phone'] == '+77009925795':
                    id_ = entity.get('id')
                    rent_days: int = (datetime.fromisoformat(entity['rent_end']).astimezone(
                        tz=timezone.utc) - datetime.fromisoformat(entity['rent_start']).astimezone(
                        tz=timezone.utc)).days
                    if rent_days > 0:
                        day_price: Decimal = Decimal(Decimal(entity['price_discount']) / rent_days)
                    else:
                        day_price = Decimal(Decimal(entity['price_discount']))

                    logger.info(f'Начали парсинг заказа {id_}')
                    rent_entity: dtos.RentEntity = dtos.RentEntity(
                        id=id_,
                        status=dtos.Status[entity['status_color'].upper()],
                        client=dtos.Client(phone=entity['client']['phone'], name=entity['client']['name']),
                        rent_start=datetime.fromisoformat(entity['rent_start']).astimezone(tz=timezone.utc),
                        rent_end=datetime.fromisoformat(entity['rent_end']).astimezone(tz=timezone.utc),
                        price=Decimal(entity['price_discount']),
                        day_price=day_price,
                        inventories=[dtos.InventoryItem(id=item['id'], name=item['inventory_name']) for item in
                                     entity['inventories']],
                        time_exceed=entity['time_exceed']

                    )

                    if rent_entity.status == dtos.Status.COMPLETED:
                        con.case_manager.completed_rent(rent_entity)
                        logger.info(f'Закончили парсинг законченного заказа {id_}')
                    else:
                        con.case_manager.new_case(rent_entity)
                        logger.info(f'Закончили парсинг заказа {id_}')

    except requests.HTTPError as err:
        logger.error(err)
        con.api_client.login()
        raise self.retry(exc=err)

    except Exception as e:
        logger.error(e)


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
        'schedule': timedelta(minutes=1)
    },
    'get-completed-rents': {
        'task': 'tasks.celery_app.get_rents',
        'schedule': timedelta(minutes=1, seconds=10),
        'kwargs': {
            'status': 4,
            'quantity': 100
        }
    },
}
