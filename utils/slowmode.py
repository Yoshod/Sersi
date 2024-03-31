from utils.base import get_page
from utils.config import Configuration
from utils.database import db_session, Slowmode


def fetch_all_slowmodes(
    config: Configuration,
    page: int,
    per_page: int,
):
    with db_session() as session:
        _query = session.query(Slowmode)

        slowmodes = _query.order_by(Slowmode.added.desc()).all()

        if not slowmodes:
            return None, 0, 0

        page_slowmodes, page, pages = get_page(slowmodes, page, per_page)
        for slowmode in page_slowmodes:
            repr(slowmode)

        return page_slowmodes, page, pages
