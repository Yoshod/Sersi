from sqlalchemy.orm import Session

import utils.database as db


def get_case_audit_logs(session: Session, case_id: str):
    return session.query(db.CasesAudit).filter_by(case_id=case_id).all()
