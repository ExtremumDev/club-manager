"""Interaction with user in private messages"""

from .suggestions import register_create_suggestion_handlers
from .dating import register_dating_handlers
from .initiative import register_create_initiative_handlers
from .account import register_account_handlers
from .events_manage import register_events_manage_handlers
from .poster import register_poster_handlers