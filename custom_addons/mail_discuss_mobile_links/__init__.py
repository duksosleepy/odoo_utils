from . import models


def post_init_hook(env):
    """Cài mới module: xử lý một loạt tin có /mail/view."""
    env["mail.message"]._mdl_bulk_inject()
