from langchain.agents import create_agent

from langchain_google_genai import (
    ChatGoogleGenerativeAI
)

from config.settings import (
    GEMINI_MODEL,
    GEMINI_TEMPERATURE
)

from config.system_prompt import (
    SYSTEM_PROMPT
)

from tools.weather_tool import (
    get_weather
)

from tools.location_tool import (
    get_location
)


def create_weather_agent(
    checkpointer
):

    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=GEMINI_TEMPERATURE
    )

    return create_agent(
        model=llm,
        tools=[
            get_weather,
            get_location
        ],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer
    )