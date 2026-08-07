from app.core.database import SessionLocal
from app.models.role import Role

DEFAULT_ROLES = [
    {"name": "user", "description": "Default role for registered users"},
    {"name": "moderator", "description": "Can moderate questions and comments"},
    {"name": "admin", "description": "Full administrative access"},
]

def seed_roles() -> None:
    db = SessionLocal()
    try:
        for role_data in DEFAULT_ROLES:
            exists = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not exists:
                db.add(Role(**role_data))
        db.commit()
        print("✓ Roles seeded")
    finally:
        db.close()

if __name__ == "__main__":
    seed_roles()
