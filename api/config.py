from os import getenv

time_to_clear = 3600

ollama_model = "gemma:1b"
ollama_host = getenv("OLLAMA_HOST", "http://localhost:11434")

session_timeout = 1800

postgres_host = getenv("POSTGRES_HOST", "localhost")
postgres_port = getenv("POSTGRES_PORT", "5432")
postgres_user = getenv("POSTGRES_USER", "postgres")
postgres_password = getenv("POSTGRES_PASSWORD", "postgres")
postgres_db = getenv("POSTGRES_DB", "app")

postgres_url = f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"