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
                f'{inventories_string}'
                f'Начало аренды: {time_start}\n'
                f'Конец аренды: {time_end}\n'
                f'Стоимость аренды: {rent_entity.price}₸\n'
                f'Номер заказа: {rent_entity.id}')

    def soon_exceed_rent_message(self, rent_entity: RentEntity) -> str:
        time_end: str = self.__convert_time(rent_entity.rent_end)
        return (f'Уважаемый клиент, близится срок сдачи оборудования.\n'
                f'Дата окончания: {time_end}\n'
                f'Номер заказа: {rent_entity.id}\n\n'
                f'Если вам необходимо продлить аренду, пожалуйста, свяжитесь с менеджером по номеру +7 (700) 860-23-00')

    def exceed_rent_message(self, rent_entity: RentEntity) -> str:
        time_end: str = self.__convert_time(rent_entity.rent_end)
        return (f'Уважаемый {rent_entity.client.name},\n'
                f'Ваш срок аренды закончился!\n'
                f'Дата окончания: {time_end}\n'
                f'Необходимо оплатить: {rent_entity.price}\n'
                f'Номер заказа: {rent_entity.id}\n\n'
                f'Для оплаты, пожалуйста, свяжитесь с менеджером по номеру +7 (700) 860-23-00')

    def exceed_penalty_rent_message(self, rent_entity: RentEntity) -> str:
        time_end: str = self.__convert_time(rent_entity.rent_end)
        return (f'Уважаемый {rent_entity.client.name},\n'
                f'Вы просрочили аренду больше чем на сутки.\n'
                f'Дата окончания: {time_end}\n'
                f'Необходимо оплатить: {rent_entity.price + rent_entity.penalty}\n'
                f'Номер заказа: {rent_entity.id}\n\n'
                f'Для оплаты, пожалуйста, свяжитесь с менеджером по номеру +7 (700) 860-23-00')

    def extended_rent_message(self, id_: int, new_rent_end: datetime) -> str:
        time_end: str = self.__convert_time(new_rent_end)
        return (f'Уважаемый клиент,\n'
                f'срок аренды продлен до {time_end}\n'
                f'Номер заказа: {id_}')

    def completed_rent_message(self) -> str:
        return (f'Уважаемый клиент, благодарим за то, что пользовались нашими услугами.\n'
                f'Если вас не затруднит, оставьте, пожалуйста, отзыв о предоставленной услуге в 2gis,\n'
                f'это поможет нам улучшить сервис и предоставлять наилучшие услуги для вас!\n'
                f'link\n\n'
                f'Помимо аренды мы занимаемся ремонтом и продажей инструментов.')

    @staticmethod
    def __get_inventories_string(inventories: list[InventoryItem] | InventoryItem) -> str:
        inventories_string: str = ''

        if isinstance(inventories, list):
            for inventory in inventories:
                inventories_string += f'-{inventory.name}\n'
        else:
            inventories_string += f'-{inventories.name}\n'

        return inventories_string

    @staticmethod
    def __convert_time(rent_end: datetime) -> str:
        kz_time: datetime = rent_end + timedelta(hours=5)
        return kz_time.strftime("%d.%m.%Y %H:%M")
