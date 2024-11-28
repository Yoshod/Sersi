import yaml

import utils.database as db


with db.db_session() as session:
    # make offences.yaml
    offences: list[db.Offence] = session.query(db.Offence).all()
    with open("files/import/offences.yaml", "w") as f:
        yaml.dump(
            [
                {
                    "offence": offence.offence,
                    "detail": offence.detail,
                    "severity": offence.warn_severity,
                    "punishments": offence.punishment_list,
                }
                for offence in offences
            ],
            f,
        )
    
    # make ticket_categories.yaml
    categories = session.query(db.TicketCategory.category).group_by(db.TicketCategory.category).all()
    subcategories: list[db.TicketCategory] = session.query(db.TicketCategory).all()
    with open("files/import/ticket_categories.yaml", "w") as f:
        yaml.dump(
            [
                {
                    "category": category[0],
                    "subcategories": [
                        subcategory.subcategory
                        for subcategory in subcategories
                        if subcategory.category == category[0]
                    ],
                }
                for category in categories
            ],
            f,
        )
