# 🌤️ Weather Agent

AI-powered weather assistant built with **Python**, **Flask**, **Gemini**, **LangChain**, and **LangGraph**.

The application automatically detects the user's location when no city is provided, retrieves real-time weather data, and maintains conversation memory using SQLite or PostgreSQL/Supabase.

![Weather Agent](docs/weather-agent.png)

---

## Features

- Real-time weather information
- Automatic location detection
- Conversation memory
- SQLite persistence
- PostgreSQL / Supabase support
- Tool calling with LangGraph
- Gemini integration
- Web chat interface with Flask
- Multi-turn conversations
- Configurable architecture

---

## Tech Stack

### Backend

- Python
- Flask
- LangChain
- LangGraph

### AI

- Gemini 2.5 Flash

### Databases

- SQLite
- PostgreSQL
- Supabase

### APIs

- OpenWeatherMap API
- IPInfo API

---

## Project Structure

```text
weather-agent/
│
├── agents/
│   └── weather_agent.py
│
├── checkpoints/
│   ├── __init__.py
│   └── checkpoint_factory.py
│
├── config/
│   ├── constants.py
│   ├── settings.py
│   └── system_prompt.py
│
├── exceptions/
│   └── configuration_error.py
│
├── tools/
│   ├── weather_tool.py
│   └── location_tool.py
│
├── utils/
│   └── response_parser.py
│
├── templates/
│   └── chat.html
│
├── static/
│   └── style.css
│
├── docs/
│   └── weather-agent.png
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/coniemenezes/weather-agent.git

cd weather-agent
```

Create and activate a virtual environment:

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file based on `.env.example`.

Example:

```env
GOOGLE_API_KEY=your_gemini_api_key

API_WEATHER=your_openweather_api_key

CHECKPOINTER_BACKEND=sqlite

SQLITE_DB_PATH=checkpoints.db

GEMINI_MODEL=gemini-2.5-flash

GEMINI_TEMPERATURE=0
```

### Optional PostgreSQL / Supabase

```env
CHECKPOINTER_BACKEND=postgres

SUPABASE_DB_URI=postgresql://postgres:password@host:5432/postgres
```

---

## Running the Application

Start the Flask application:

```bash
python app.py
```

Open your browser:

```text
http://127.0.0.1:5000
```

---

## How It Works

### Weather Requests

User:

```text
What's the weather today?
```

Agent workflow:

```text
get_location()
        ↓
get_weather(city)
        ↓
Generate response
```

### Weather Requests With City

User:

```text
What's the weather in Rome?
```

Agent workflow:

```text
get_weather("Rome")
        ↓
Generate response
```

---

## Persistence

The project supports:

### SQLite

Ideal for local development.

```env
CHECKPOINTER_BACKEND=sqlite
```

### PostgreSQL / Supabase

Ideal for production deployments.

```env
CHECKPOINTER_BACKEND=postgres
```

Conversation history is automatically stored through LangGraph checkpoints.

---

## Example Conversation

```text
User:
What's the temperature today?

Assistant:
In Lisbon, Portugal, the temperature is 23.8°C with clear skies.
Humidity is 69% and wind speed is 5.81 km/h.
```

---

## Future Improvements

- Weather forecast support
- Multiple language support
- User geolocation from browser
- Docker deployment
- Streamlit version
- Authentication
- Weather alerts

---

## Author

**Conie Menezes**

GitHub:

https://github.com/coniemenezes

Project Repository:

https://github.com/coniemenezes/weather-agent

---

## License

This project is licensed under the MIT License.