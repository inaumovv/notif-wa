from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP

from helpers.DTOs import RentEntity, Status
from services.message_sender import MessageSender
from services.message_text import MessageText
from services.payment_api_client import PaymentApiClient
from services.redis import Redis


class CaseManager:

    def __init__(
            self,
            redis: Redis,
            message_sender: MessageSender,
            message_text: MessageText,
            payment_api_client: PaymentApiClient,
    ):
        self.redis = redis
        self.message_sender = message_sender
        self.message_text = message_text
        self.payment_api_client = payment_api_client

    def new_case(self, rent_entity: RentEntity) -> None:
        new_rent: dict = self.new_rent(rent_entity)
        if not new_rent['new']:
            rent_db: RentEntity = new_rent['data']
            self.extended_rent(rent_entity, rent_db)
            self.soon_exceed_rent(rent_entity, rent_db)
            self.exceed_rent(rent_entity, rent_db)

    def new_rent(self, rent_entity: RentEntity) -> dict:
        rent_db: dict = self.redis.get(rent_entity.id)

        if not rent_db:
            self.__send_new_rent_notification(rent_entity)
            return {'new': True, 'data': None}

        return {'new': False, 'data': RentEntity(**rent_db)}

    def completed_rent(self, rent_entity: RentEntity) -> None:
        rent_db: dict | None = self.redis.get(rent_entity.id)
        if rent_db:
            self.redis.delete(rent_entity.id)
            message_text: str = self.message_text.completed_rent_message()
            self.message_sender.send_message(
                number=rent_entity.client.phone[1:],  # номер телефона без +
                message=message_text
            )

    def __send_new_rent_notification(self, rent_entity: RentEntity) -> None:
        self.redis.set(rent_entity.id, rent_entity.json())
        message_text: str = self.message_text.new_rent_message(rent_entity)
        self.message_sender.send_message(
            number=rent_entity.client.phone[1:],  # номер телефона без +
            message=message_text
        )

    def exceed_rent(self, rent_entity: RentEntity, rent_db: RentEntity) -> None:
        if rent_entity.time_exceed:
            last_hour_exceed_notifications: datetime | None = rent_db.last_exceed_notification.every_3_hours
            last_day_exceed_notifications: datetime | None = rent_db.last_exceed_notification.every_day

            if last_hour_exceed_notifications:
                interval_hours: timedelta = datetime.now(tz=timezone.utc) - last_hour_exceed_notifications
                if interval_hours >= timedelta(hours=3):
                    self.__send_exceed_notification(rent_entity)
            else:
                self.__send_exceed_notification(rent_entity)

            if last_day_exceed_notifications:
                interval_days: timedelta = datetime.now(tz=timezone.utc) - last_day_exceed_notifications
            else:
                interval_days: timedelta = datetime.now(tz=timezone.utc) - rent_entity.rent_end

            if interval_days.days >= 1:
                self.__send_penalty_notification(rent_entity)

    def __send_exceed_notification(self, rent_entity: RentEntity) -> None:
        rent_entity.last_exceed_notification.every_3_hours = datetime.now(tz=timezone.utc)
        self.redis.set(rent_entity.id, rent_entity.json())
        message_text: str = self.message_text.exceed_rent_message(rent_entity)
        self.message_sender.send_message(number=rent_entity.client.phone[1:], message=message_text)

    @staticmethod
    def __calculate_penalty(rent_entity: RentEntity) -> Decimal:
        rent_days: int = (rent_entity.rent_end - rent_entity.rent_start).days
        one_day_price: Decimal = rent_entity.price / rent_days
        exceed_days: int = (datetime.now(tz=timezone.utc) - rent_entity.rent_end).days
        penalty: Decimal = (exceed_days * one_day_price).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        return penalty

    def __send_penalty_notification(self, rent_entity: RentEntity) -> None:
        rent_entity.penalty = self.__calculate_penalty(rent_entity)
        rent_entity.last_exceed_notification.every_day = datetime.now(tz=timezone.utc)
        self.redis.set(rent_entity.id, rent_entity.json())
        message_text: str = self.message_text.exceed_penalty_rent_message(rent_entity)
        self.message_sender.send_message(number=rent_entity.client.phone[1:], message=message_text)

    def soon_exceed_rent(self, rent_entity: RentEntity, rent_db: RentEntity) -> None:
        if rent_db.status != Status.SOON_EXCEED:
            self.__send_soon_exceed_notification(rent_entity)

    def __send_soon_exceed_notification(self, rent_entity: RentEntity) -> None:
        time_difference: timedelta = abs(rent_entity.rent_end - datetime.now(tz=timezone.utc))
        if time_difference <= timedelta(hours=2):
            rent_entity.status = Status.SOON_EXCEED
            self.redis.set(rent_entity.id, rent_entity.json())
            message_text: str = self.message_text.soon_exceed_rent_message(rent_entity)
            self.message_sender.send_message(number=rent_entity.client.phone[1:], message=message_text)

    def extended_rent(self, rent_entity: RentEntity, rent_db: RentEntity) -> None:
        if rent_db.rent_end < rent_entity.rent_end:
            self.redis.set(rent_entity.id, rent_entity.json())
            message_text: str = self.message_text.extended_rent_message(rent_entity.id, rent_entity.rent_end)
            self.message_sender.send_message(number=rent_entity.client.phone[1:], message=message_text)
