from enum import Enum


from text import (
    get_french_club_card_text,
    get_business_meet_card_text,
    get_table_game_card_text,
    get_women_meets_card_text, get_excursion_card_text,
)


class EventType(Enum):
    FRENCH_CLUB = 0
    TABLE_GAMES = 1
    BUISNESS_MEETS = 2
    WOMEN_MEETS = 3
    INITIATIVE = 4
    EXCURSIONS = 5


    def get_card_text(self, **kwargs):
        functions = {
            EventType.FRENCH_CLUB: get_french_club_card_text,
            EventType.BUISNESS_MEETS: get_business_meet_card_text,
            EventType.TABLE_GAMES: get_table_game_card_text,
            EventType.WOMEN_MEETS: get_women_meets_card_text,
            EventType.EXCURSIONS: get_excursion_card_text

        }

        return functions[self](**kwargs)



    def get_event_name(self):
        match (self):
            case (EventType.FRENCH_CLUB):
                return "🇫🇷 Разговорный французский клуб"
            case (EventType.BUISNESS_MEETS):
                return "💼 Мастермайнды / Бизнес"
            case (EventType.WOMEN_MEETS):
                return "☕️ Женские психологические встречи"
            case (EventType.TABLE_GAMES):
                return "🎲 Настольные игры"
            case(EventType.EXCURSIONS):
                return "Экскурсии / Путешествия / Спорт"


class Sex(Enum):
    MALE = 0
    FEMALE = 1
