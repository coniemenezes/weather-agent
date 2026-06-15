from dotenv import load_dotenv

from agents.weather_agent import (
    create_weather_agent
)

from checkpoints.checkpoint_factory import (
    create_checkpointer
)

from utils.response_parser import (
    extract_text_from_response
)

from config.constants import (
    EXIT_COMMANDS
)

from config.settings import (
    THREAD_ID,
    CHECKPOINTER_BACKEND
)

load_dotenv()


def should_exit(
    user_query: str
) -> bool:

    return (
        user_query.lower().strip()
        in EXIT_COMMANDS
    )


def run_chat():

    with create_checkpointer() as checkpointer:

        backend = (
            CHECKPOINTER_BACKEND
            .lower()
            .strip()
        )

        if (
            backend in {
                "supabase",
                "postgres",
                "postgresql"
            }
            and hasattr(
                checkpointer,
                "setup"
            )
        ):
            checkpointer.setup()

        agent = create_weather_agent(
            checkpointer
        )

        config = {
            "configurable": {
                "thread_id": THREAD_ID
            }
        }

        print("\nWeather Assistant\n")

        while True:

            user_query = input(
                "Você: "
            ).strip()

            if not user_query:
                continue

            if should_exit(
                user_query
            ):
                print(
                    "\nAssistente: Até logo."
                )
                break

            response = agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_query
                        }
                    ]
                },
                config
            )

            print(
                f"\nAssistente: "
                f"{extract_text_from_response(response)}\n"
            )


if __name__ == "__main__":
    run_chat()