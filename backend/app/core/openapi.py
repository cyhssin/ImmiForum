from fastapi.openapi.utils import get_openapi

# Single source of truth for "Try it out" examples, injected by schema name.
# Unknown names are skipped silently, so this is safe to extend — including
# for auth schemas whose exact class names you can confirm with:
#   docker compose exec backend python -c \
#     "from app.main import app; print(sorted(app.openapi()['components']['schemas']))"
EXAMPLES: dict[str, dict] = {
    "QuestionCreate": {
        "title": "How long does family reunification take?",
        "body": "I applied in March and am still waiting. Is 6 months normal?",
        "tag_names": ["visa", "family"],
        "category_id": None,
    },
    "QuestionUpdate": {
        "title": "How long does family reunification really take?",
        "tag_names": ["visa", "family", "timeline"],
    },
    "CommentCreate": {
        "body": "Mine took 3 months — check the processing times page.",
        "parent_id": None,
    },
    "CommentUpdate": {
        "body": "Edit: it took 3 months total, approved last week.",
    },
    "UserUpdate": {
        "username": "cyhssin",
        "bio": "Immigrant, sharing my visa journey.",
        "avatar_url": "https://example.com/avatar.png",
    },
    "PasswordChange": {
        "current_password": "OldSecret123",
        "new_password": "NewSecret456",
    },
    "UserStatusUpdate": {"is_active": False},
    "UserRoleUpdate": {"role": "moderator"},
    # ── Safe guesses below: ignored if the schema name doesn't exist ──
    "LoginRequest": {"username": "hssininuse@gmail.com", "password": "Secret123"},
    "UserLogin": {"username": "hssininuse@gmail.com", "password": "Secret123"},
    "RegisterRequest": {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "Secret123",
    },
    "UserCreate": {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "Secret123",
    },
}

def build_custom_openapi(app):
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=app.openapi_tags,
        )

        components = schema.get("components", {}).get("schemas", {})
        for name, example in EXAMPLES.items():
            if name in components:
                components[name]["example"] = example

        app.openapi_schema = schema
        return schema

    return custom_openapi