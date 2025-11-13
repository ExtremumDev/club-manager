from datetime import datetime


def get_activity_suggestion_text(name, description, date: str, place, username):
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
📅 {date.strftime("%d-%m-%Y %H:%M")}  
🏃‍♀️ Тип активности: {activity_type}
💬 {comment}      
"""


def get_french_club_card_text(date_time, place, description, members_left, holder, **kwargs):
    return f"""
🇫🇷 Разговорный клуб
🗣 Ведущий - {holder}
📍 {place}
📅 {date_time.strftime("%d-%m-%Y %H:%M")}  
👥 Мест осталось: {members_left}
💬 {description}
"""


def get_women_meets_card_text(date_time, place, description, members_left, holder, **kwargs):
    return f"""
☕️ Женская психологическая встреча
🗣 Ведущий - {holder}
📍 {place}
📅 {date_time.strftime("%d-%m-%Y %H:%M")}  
👥 Мест осталось: {members_left}  
💬 {description}
"""

def get_buisness_meet_card_text(date_time, place, description, members_left, holder, **kwargs):
    return f"""
💼 Мастермайнды / Бизнес
🗣 Ведущий - {holder}
📍 {place}
📅 {date_time.strftime("%d-%m-%Y %H:%M")}  
👥 Мест осталось: {members_left}
💬 {description}
"""


def get_table_game_card_text(activity_name, date_time, place, description, members_left, holder, **kwargs):
    return f"""
🎲 {activity_name}
🗣 Ведущий - {holder}
📍 {place}
📅 {date_time.strftime("%d-%m-%Y %H:%M")}
👥 Мест {members_left}
💬 {description}
"""


def get_account_description(rating: int, user_name: str, alias: str, reg_date: datetime, interests, city):
    return f"""
Имя: {user_name}
Псевдоним: {alias}
Город: {city}

Дата регистрации: {reg_date.strftime("%d-%m-%Y %H:%M")}

Интересы: {interests}

Мои баллы: {rating}

Мероприятий посещено: {0}

"""


two_hours_before_text_french = "Встречаемся через 2 часа! Не опаздывайте, проверьте расписание своего транспорта🙏"
day_before_text_french = "Завтра встреча клуба французского! 🇫🇷 Готовим береты!"

two_hours_before_text_women = "Встречаемся через 2 часа! Не опаздывайте, проверьте расписание своего транспорта🙏"
day_before_text_women = "Завтра встречаемся с девочками! Берем с собой всё свое тепло☀️"

two_hours_before_text_business = "Встречаемся через 2 часа! Не опаздывайте, проверьте расписание своего транспорта🙏"
day_before_text_business = "Завтра особый день - найдется решение мучающего вопроса! Фиксируйте в заметках запрос и будьте готовы к мозговому штурму😅"