# -*- coding: utf-8 -*-
"""Migration 19.0.1.0.34 — rebalance được chạy sau khi toàn bộ module đã load.

Không gọi rebalance trong post-migrate vì lúc này các module phụ thuộc
(time_off_work_handover, …) có thể chưa đăng ký field → write() gây lỗi.
Rebalance chạy một lần qua script sau khi cập nhật module xong.
"""

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info(
        "hr_leave_type_mien 19.0.1.0.34: bỏ qua rebalance trong post-migrate "
        "(sẽ chạy sau khi cập nhật module hoàn tất)"
    )
