from config.settings import Settings

def test_urls_generated_correctly():
    s = Settings(
        RABBIT_HOST="localhost",
        RABBIT_PORT=5672,
        RABBIT_USER="u",
        RABBIT_PASSWORD="p",
        DB_HOST="db",
        DB_PORT=5432,
        DB_NAME="name",
        DB_USER="user",
        DB_PASSWORD="pass",
        REDIS_HOST="redis",
        REDIS_PORT=6379,
        GIT_SECRET="secret",
        GOOGLE_SERVICE_ACCOUNT_JSON="x.json",
        GOOGLE_CALENDAR_SCOPES="scope",
    )

    assert s.db_url.startswith("postgresql+asyncpg://")
    assert s.rabbit_url.startswith("amqp://")
    assert s.redis_url == "redis://redis:6379/0"
