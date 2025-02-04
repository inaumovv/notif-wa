from datetime import datetime, timezone, timedelta
from decimal import Decimal

from helpers.DTOs import InventoryItem, RentEntity


class MessageText:

    def new_rent_message(self, rent_entity: RentEntity) -> str:
        time_end: str = self.__convert_time(rent_entity.rent_end)
        time_start: str = self.__convert_time(rent_entity.rent_start)
        inventories_string: str = self.__get_inventories_string(rent_entity.inventories)
        return (f'Здравствуйте, '
                f'{rent_entity.client.name}.\n'
                f'Вы арендовали:\n'
                f'{inventories_string}\n'
                f'Начало аренды: {time_start}\n'
                f'Конец аренды: {time_end}\n'
                f'Стоимость аренды в сутки (24 часа): {rent_entity.day_price}₸\n'
                f'Номер заказа: {rent_entity.id}\n\n'
                f'Правила пользования оборудования:\n'
                f'- Клиент несет ответственность за внешнее состояние оборудования (отсутствие внешних повреждений)\n'
                f'- Выдача и возврат оборудования производится в чистом виде (нужно протереть после работы)\n'
                f'- Оплата и продление оборудования производится заранее')

    def soon_exceed_rent_message(self, rent_entity: RentEntity) -> str:
        time_end: str = self.__convert_time(rent_entity.rent_end)
        inventories_string: str = self.__get_inventories_string(rent_entity.inventories)
        return (f'Уважаемый клиент, близится срок сдачи оборудования.\n'
                f'Дата окончания: {time_end}\n'
                f'Номер заказа: {rent_entity.id}\n\n'
                f'Инструмент:\n'
                f'{inventories_string}\n'
                f'Для продления просим связаться с менеджером по номеру +7 (771) 360-26-92')

    def exceed_rent_message(self, rent_entity: RentEntity) -> str:
        inventories_string: str = self.__get_inventories_string(rent_entity.inventories)
        return (f'Уважаемый {rent_entity.client.name},\n'
                f'срок аренды оборудования закончился.\n'
                f'Вам необходимо внести оплату за оборудование:\n'
                f'{inventories_string}\n'
                f'Номер заказа: {rent_entity.id}\n\n'
                f'Для оплаты свяжитесь с менеджером по номеру +7 (700) 860-23-00')

    def exceed_penalty_rent_message(self, rent_entity: RentEntity) -> str:
        time_end: str = self.__convert_time(rent_entity.rent_end)
        return (f'Уважаемый {rent_entity.client.name},\n'
                f'Вы просрочили аренду больше чем на сутки.\n'
                f'Дата окончания: {time_end}\n'
                f'Необходимо оплатить: {rent_entity.price + rent_entity.penalty}₸\n'
                f'Номер заказа: {rent_entity.id}\n\n'
                f'Для оплаты, пожалуйста, свяжитесь с менеджером по номеру +7 (771) 360-26-92')

    def extended_rent_message(self, id_: int, new_rent_end: datetime) -> str:
        time_end: str = self.__convert_time(new_rent_end)
        return (f'Уважаемый клиент,\n'
                f'Вы успешно продлили аренду.\n'
                f'Новый срок сдачи: {time_end}\n'
                f'Номер заказа: {id_}')

    def completed_rent_message(self) -> str:
        return (f'Оборудование возвращено без повреждений и дефектов.\n'
                f'Спасибо за выбор нашей компании PRORENT.kz\n'
                f'Будем благодарны за оставленный отзыв о нашей работе в 2гис, это помогает нам стать лучше.')

    @staticmethod
    def __get_inventories_string(inventories: list[InventoryItem] | InventoryItem) -> str:
        inventories_string: str = ''

        if isinstance(inventories, list):
            for inventory in inventories:
                inventories_string += f'-{inventory.name} (инвентарный номер {inventory.id})\n'
        else:
            inventories_string += f'-{inventories.name}\n'

        return inventories_string

    @staticmethod
    def __convert_time(rent_end: datetime) -> str:
        kz_time: datetime = rent_end + timedelta(hours=5)
        return kz_time.strftime("%d.%m.%Y %H:%M")
