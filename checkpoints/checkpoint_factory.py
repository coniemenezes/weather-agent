import os

from config.settings import (
    CHECKPOINTER_BACKEND,
    SQLITE_DB_PATH,
    SUPABASE_DB_URI
)

from exceptions.configuration_error import (
    ConfigurationError
)

def create_checkpointer():

    backend = CHECKPOINTER_BACKEND.lower()

    if backend == "sqlite":

        from langgraph.checkpoint.sqlite import (
            SqliteSaver
        )

        return SqliteSaver.from_conn_string(
            SQLITE_DB_PATH
        )

    if backend in {
        "supabase",
        "postgres",
        "postgresql"
    }:

        from langgraph.checkpoint.postgres import (
            PostgresSaver
        )

        if not SUPABASE_DB_URI:
            raise ConfigurationError(
                "SUPABASE_DB_URI não configurada."
            )

        return PostgresSaver.from_conn_string(
            SUPABASE_DB_URI
        )

    raise ConfigurationError(
        "Backend inválido."
    )