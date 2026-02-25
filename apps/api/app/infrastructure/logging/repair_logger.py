"""비동기 수리 로그 — blocking I/O 없는 async 구현"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


async def log_repair_iteration(rule_code: str | None, node_id: str | None) -> None:
    """
    수리 반복 로그를 Python logging으로 기록한다.
    기존 generator.py의 blocking open() 호출을 대체.
    """
    logger.debug(
        "[repair] rule_code=%s, node_id=%s, ts=%s",
        rule_code,
        node_id,
        datetime.now(timezone.utc).isoformat(),
    )
