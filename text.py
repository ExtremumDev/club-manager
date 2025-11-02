from utils.enums import EventType


def get_activity_suggestion_text(name, description, date, place, username):
    return f"""
Новое предложение активности от пользователя @{username}
Название: {name}

{description}

Дата и время: {date}
Место встречи: {place}
"""

def get_dating_profile_descr(alias, description, username):
    return f"""
{alias}

{description}

@{username}
"""


def get_initiative_text(date, place, comment, activity_type):
    return f"""
Инициатива
📍 {place}  
📅 {date}  
🏃‍♀️ Тип активности: {activity_type}
💬 {comment}      
"""


def get_french_club_card_text(date, place, description, memebers_left):
    return f"""
💼  Мастермайнд
📍 {place}
📅 {date}  
👥 Мест осталось: {members_left}  
💬 {description}
"""


def get_women_meets_card_text(date, place, description, memebers_left):
    return f"""
☕️ Женская психологическая встреча
📍 {place}
📅 {date}  
👥 Мест осталось: {members_left}  
💬 {description}
"""

def get_buisness_meet_card_text(date, place, description, memebers_left):
    return f"""
🇫🇷 Разговорный клуб  
📍 {place}
📅 {date}  
👥 Мест осталось: {members_left}
💬 {description}
"""


def get_event_name(event_type: EventType):
    match (event_type):
        case (EventType.FRENCH_CLUB):
            return "🇫🇷 Разговорный французский клуб"
        case (EventType.BUISNESS_MEETS):
            return "💼 Мастермайнды / Бизнес"
        case (EventType.WOMEN_MEETS):
            return "☕️ Женские психологические встречи"
    # end match
