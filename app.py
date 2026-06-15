from flask import Flask, render_template, request, redirect, url_for, session
import uuid
import atexit

from agents.weather_agent import create_weather_agent
from checkpoints.checkpoint_factory import create_checkpointer
from utils.response_parser import extract_text_from_response
from config.settings import CHECKPOINTER_BACKEND

app = Flask(__name__)
app.secret_key = "weather-agent-secret"

checkpointer_context = create_checkpointer()
checkpointer = checkpointer_context.__enter__()

backend = CHECKPOINTER_BACKEND.lower().strip()

if backend in {"supabase", "postgres", "postgresql"} and hasattr(checkpointer, "setup"):
    checkpointer.setup()

agent = create_weather_agent(checkpointer)


@atexit.register
def close_checkpointer():
    checkpointer_context.__exit__(None, None, None)


@app.route("/")
def home():
    if "thread_id" not in session:
        session["thread_id"] = str(uuid.uuid4())

    if "messages" not in session:
        session["messages"] = []

    return render_template("chat.html", messages=session["messages"])


@app.route("/send", methods=["POST"])
def send():
    user_message = request.form.get("message", "").strip()

    if not user_message:
        return redirect(url_for("home"))

    try:
        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_message}]},
            {"configurable": {"thread_id": session["thread_id"]}}
        )

        assistant_message = extract_text_from_response(response)

    except Exception as e:
        assistant_message = f"Erro: {e}"

    session["messages"].append({
        "type": "human",
        "content": user_message
    })

    session["messages"].append({
        "type": "ai",
        "content": assistant_message
    })

    session.modified = True

    return redirect(url_for("home"))


@app.route("/clear")
def clear():
    session["thread_id"] = str(uuid.uuid4())
    session["messages"] = []
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)