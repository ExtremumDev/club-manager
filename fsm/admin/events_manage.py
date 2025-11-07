from aiogram.fsm.state import State, StatesGroup


class CreateEventFSM(StatesGroup):
    date_time_state = State()
    place_state = State()
    descr_state = State()
    members_limit_state = State()
    game_name_state = State()


class NewEventMemberFSM(StatesGroup):
    member_name_state = State()
