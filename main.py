"""
Weather Assistant - versão final
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
IPINFO_URL = "https://ipinfo.io/json"
REQUEST_TIMEOUT = 10

EXIT_COMMANDS = {
    "exit",
    "quit",
    "bye",
    "goodbye",
    "adeus",
    "tchau",
    "até logo",
    "ate logo",
    "falou",
    "encerrar",
    "sair",
    "fui",
    "xau",
    "vlw",
    "obrigada",
    "obrigado",
}

COUNTRIES = {
    "PT": "Portugal",
    "BR": "Brazil",
    "US": "United States",
    "ES": "Spain",
    "FR": "France",
    "IT": "Italy",
    "DE": "Germany",
    "LR": "Liberia",
    "MM": "Myanmar",
}

FAHRENHEIT_COUNTRIES = {
    "United States",
    "Liberia",
    "Myanmar",
}


class ConfigurationError(Exception):
    """Erro de configuração do projeto."""


def get_env(name: str, required: bool = False, default: Optional[str] = None) -> Optional[str]:
    """Obtém uma variável de ambiente com validação opcional."""
    value = os.getenv(name, default)

    if required and not value:
        raise ConfigurationError(f"Variável de ambiente obrigatória não encontrada: {name}")

    return value


def get_weather(city: str) -> Dict[str, Any]:
    """
    Get weather for a given city.

    Use this tool when the user asks about weather and provides a city/location.
    """
    api_key = get_env("API_WEATHER", required=True)

    if not city or not city.strip():
        return {
            "error": "Cidade não informada. Informe uma cidade válida para consultar o clima."
        }

    try:
        response = requests.get(
            OPENWEATHER_URL,
            params={
                "q": city.strip(),
                "appid": api_key,
                "units": "metric",
                "lang": "pt_br",
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        wind = data.get("wind", {})
        sys_data = data.get("sys", {})

        temp_c = main.get("temp")
        temp_f = round((temp_c * 9 / 5) + 32, 2) if isinstance(temp_c, (int, float)) else None

        country_code = sys_data.get("country", "")
        country_name = COUNTRIES.get(country_code, country_code)
        preferred_unit = "fahrenheit" if country_name in FAHRENHEIT_COUNTRIES else "celsius"

        return {
            "city": data.get("name", city),
            "country": country_name,
            "condition": weather.get("description", "Não informado"),
            "temperature_celsius": temp_c,
            "temperature_fahrenheit": temp_f,
            "preferred_unit": preferred_unit,
            "humidity": main.get("humidity"),
            "wind_speed": wind.get("speed"),
        }

    except requests.exceptions.HTTPError as exc:
        status_code = exc.response.status_code if exc.response else "desconhecido"

        if status_code == 401:
            return {
                "error": "A chave da API OpenWeatherMap está inválida ou ausente. Verifique API_WEATHER no arquivo .env."
            }

        if status_code == 404:
            return {
                "error": f"Não encontrei dados de clima para '{city}'. Verifique se o nome da cidade está correto."
            }

        return {
            "error": f"Erro HTTP ao consultar o clima. Status: {status_code}. Detalhe: {exc}"
        }

    except requests.exceptions.RequestException as exc:
        return {
            "error": f"Erro de conexão ao consultar o clima: {exc}"
        }

    except (KeyError, TypeError, ValueError) as exc:
        return {
            "error": f"A resposta da API de clima veio em formato inesperado: {exc}"
        }


def get_location() -> str:
    """
    Get user's current location.

    Use this tool when the user asks about weather without specifying a city.
    """
    try:
        response = requests.get(
            IPINFO_URL,
            headers={"User-Agent": "weather-assistant"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        city = data.get("city")
        country_code = data.get("country", "")
        country_name = COUNTRIES.get(country_code, country_code)

        if not city:
            return "Lisbon, Portugal"

        return f"{city}, {country_name}"

    except requests.exceptions.RequestException:
        return "Lisbon, Portugal"


def create_llm() -> ChatGoogleGenerativeAI:
    """Cria o modelo Gemini usado pelo agente."""
    model = get_env("GEMINI_MODEL", default="gemini-2.5-flash")
    temperature_raw = get_env("GEMINI_TEMPERATURE", default="0")

    try:
        temperature = float(temperature_raw or 0)
    except ValueError:
        temperature = 0

    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
    )


def get_system_prompt() -> str:
    """Prompt principal do agente."""
    return """
You are a helpful weather assistant.

WORKFLOW:

1. If the user asks about weather without providing a city:
   - Call get_location()
   - Then call get_weather(city) using the location returned by get_location()

2. If the user provides a city:
   - Call get_weather(city) directly.

3. Use Celsius for most countries.

4. Use Fahrenheit for:
   - United States
   - Liberia
   - Myanmar

5. Always present:
   - City and country
   - Temperature
   - Weather condition
   - Humidity
   - Wind speed

6. If a tool returns an error field, explain the error clearly and briefly.

7. Answer naturally and concisely in the same language used by the user.
"""


def create_checkpointer():
    """
    Cria o checkpointer de acordo com CHECKPOINTER_BACKEND.

    Valores aceitos:
    - sqlite
    - supabase
    - postgres
    """
    backend = (get_env("CHECKPOINTER_BACKEND", default="sqlite") or "sqlite").lower().strip()

    if backend == "sqlite":
        from langgraph.checkpoint.sqlite import SqliteSaver

        db_path = get_env("SQLITE_DB_PATH", default="checkpoints.db")
        return SqliteSaver.from_conn_string(db_path)

    if backend in {"supabase", "postgres", "postgresql"}:
        from langgraph.checkpoint.postgres import PostgresSaver

        db_uri = get_env("SUPABASE_DB_URI", required=True)
        return PostgresSaver.from_conn_string(db_uri)

    raise ConfigurationError(
        "CHECKPOINTER_BACKEND inválido. Use 'sqlite' ou 'supabase'."
    )


def extract_text_from_response(response: Dict[str, Any]) -> str:
    """Extrai o texto final da resposta do agente de forma segura."""
    messages = response.get("messages", [])

    if not messages:
        return "Não consegui gerar uma resposta."

    content = messages[-1].content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []

        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if text:
                    text_parts.append(str(text))
            elif isinstance(item, str):
                text_parts.append(item)

        if text_parts:
            return "\n".join(text_parts)

    return str(content)


def should_exit(user_query: str) -> bool:
    """Verifica se o usuário quer encerrar a conversa."""
    normalized_query = user_query.lower().strip()
    return normalized_query in EXIT_COMMANDS


def run_chat() -> None:
    """Executa o chat no terminal."""
    llm = create_llm()
    system_prompt = get_system_prompt()
    thread_id = get_env("THREAD_ID", default="weather-session")

    with create_checkpointer() as checkpointer:
        backend = (get_env("CHECKPOINTER_BACKEND", default="sqlite") or "sqlite").lower().strip()

        if backend in {"supabase", "postgres", "postgresql"} and hasattr(checkpointer, "setup"):
            checkpointer.setup()

        agent = create_agent(
            model=llm,
            tools=[get_weather, get_location],
            system_prompt=system_prompt,
            checkpointer=checkpointer,
        )

        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        print("\nWeather Assistant")
        print("Pergunte sobre o clima de uma cidade ou pergunte apenas 'como está o clima?'.")
        print("Digite 'sair', 'tchau', 'bye', 'exit' ou 'quit' para encerrar.\n")

        while True:
            user_query = input("Você: ").strip()

            if not user_query:
                print("\nAssistente: Escreva uma pergunta para eu consultar o clima.\n")
                continue

            if should_exit(user_query):
                print("\nAssistente: Até logo.")
                break

            try:
                response = agent.invoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": user_query,
                            }
                        ]
                    },
                    config,
                )

                print(f"\nAssistente: {extract_text_from_response(response)}\n")

            except ConfigurationError as exc:
                print(f"\nErro de configuração: {exc}\n")

            except Exception as exc:
                print("\nErro inesperado ao processar a pergunta:")
                print(exc)
                print()


if __name__ == "__main__":
    try:
        run_chat()
    except ConfigurationError as exc:
        print(f"Erro de configuração: {exc}")
