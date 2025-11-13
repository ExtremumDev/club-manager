from .private import *
from .group import *

from .start import register_user_start_handlers


def register_user_handlers(dp):
    register_user_start_handlers(dp)

    register_event_membership_handlers(dp)

    register_account_handlers(dp)
    register_dating_handlers(dp)
    register_create_initiative_handlers(dp)
    register_create_suggestion_handlers(dp)
    register_events_manage_handlers(dp)
    register_poster_handlers(dp)
