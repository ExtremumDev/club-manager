from aiogram.fsm.state import State, StatesGroup


class SuggestActivityFSM(StatesGroup):
    name_state = State()
    descr_state = State()
    date_state = State()
    place_state = State()


class CreateDatingProfileFSM(StatesGroup):
    profile_photo_state = State()
    description_state = State()
    interests_state = State()
    goal_state = State()


class CreateInitiativeFSM(StatesGroup):
    date_state = State()
    place_state = State()
    comment_state = State()


class RegistrationFSM(StatesGroup):
    name_state = State()
    profile_photo_state = State()
    social_link_state = State()
    sex_state = State()
    interests_state = State()
    goal_state = State()
    photo_state = State()


class UpdateProfileFSM(StatesGroup):
    key_state = State()
    value_state = State()
