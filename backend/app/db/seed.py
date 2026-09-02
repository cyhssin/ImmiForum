from app.core.database import SessionLocal
from app.models.role import Role

DEFAULT_ROLES = [
    {
        "name": "user",
        "description": "Default role for registered users",
        "permissions": [
            "create_question",
            "create_comment",
            "like_question",
            "bookmark_question",
            "follow_user",
        ],
    },
    {
        "name": "moderator",
        "description": "Can moderate questions and comments",
        "permissions": [
            "create_question",
            "create_comment",
            "like_question",
            "bookmark_question",
            "follow_user",
            "close_question",
            "pin_question",
            "delete_comment",
        ],
    },
    {
        "name": "admin",
        "description": "Full administrative access",
        "permissions": [
            "create_question",
            "create_comment",
            "like_question",
            "bookmark_question",
            "follow_user",
            "close_question",
            "pin_question",
            "delete_comment",
            "delete_question",
            "manage_users",
            "manage_roles",
        ],
    },
]

def seed_roles() -> None:
    db = SessionLocal()
    try:
        for role_data in DEFAULT_ROLES:
            existing = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing:
                db.add(Role(**role_data))
            else:
                # Update permissions if role already exists
                existing.permissions = role_data["permissions"]
                existing.description = role_data["description"]
        db.commit()
        print("✓ Roles seeded")
    finally:
        db.close()

if __name__ == "__main__":
    seed_roles()
