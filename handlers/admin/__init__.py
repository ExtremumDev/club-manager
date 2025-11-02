from .start import register_start_handlers
from .events import register_create_event_handlers
from .inititatives import register_manage_initiative_handlers


def register_admin_handlers(dp):
    register_start_handlers(dp)
    register_create_event_handlers(dp)
    register_manage_initiative_handlers(dp)
