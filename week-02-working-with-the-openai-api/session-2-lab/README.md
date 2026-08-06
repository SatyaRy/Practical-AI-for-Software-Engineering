# Configurable Text Assistant — Lab 2

Practical AI for Software Engineering · Week 2 · Lab 2

A command-line assistant built on the Chat Completions API. Its persona,
temperature, output length, and streaming behaviour are all configurable, and
it handles API failures gracefully instead of crashing.

> This is a **reference implementation**. If you are a student, your task is to
> build the equivalent yourself starting from your Lab 1 AskBot — use this only
> the way your instructor tells you to.

## Project layout

```
askbot/
├── main.py            # CLI, input/output loop, interactive commands
├── llm.py             # LLM service wrapper (errors, retries, usage)
├── config.py          # defaults + personas
├── store.py           # SQLite persistence for /save and /load (S2)
├── requirements.txt   # dependencies
├── .env.example       # template for your key (copy to .env)
├── .gitignore         # ignores .env, .venv, __pycache__, *.db
└── README.md          # this file
```

The flow of control is a straight line:
`main.py → conversation logic → LLM service (llm.py) → OpenAI API`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate           # Windows

pip install -r requirements.txt

cp .env.example .env               # then edit .env and add your real key
```

Set the model name in `config.py` (`DEFAULT_MODEL`) to whatever your course
environment provides, or export `API_MODEL`.

## Running

```bash
python main.py
python main.py --persona tutor
python main.py --persona reviewer --temperature 0.2
python main.py --persona tutor --temperature 0.4 --max-tokens 500 --stream
```

### Flags

| Flag            | Default | Description                          |
| --------------- | ------- | ------------------------------------ |
| `--persona`     | default | tutor · reviewer · interviewer       |
| `--temperature` | 0.7     | 0.0 (focused) → 2.0 (varied)         |
| `--max-tokens`  | 500     | maximum length of the reply          |
| `--model`       | YOUR_MODEL | override the model name           |
| `--stream`      | off     | show the reply progressively         |

### Interactive commands

```
/help        /persona <name>     /temperature <value>
/tokens <n>  /usage              /clear            /quit
/save <name> /load <name>        (S2: save and resume chats)
```

## How the requirements map to the code

| Req | Where |
| --- | ----- |
| R1  API integration   | `llm.py` → `LLMService.ask` / `stream` |
| R2  Persona           | `config.py` personas + `--persona`     |
| R3  Temperature       | `--temperature`, `/temperature`        |
| R4  Output limit      | `--max-tokens`, `/tokens`              |
| R5  Conversation memory | `main.py` → `Session.messages`       |
| R6  Error handling    | `llm.py` error classes + friendly messages |
| R7  Token tracking    | `llm.py` → `Usage`, printed each turn  |
| R8  Streaming         | `llm.py` → `stream`, `--stream`        |
| R9  Security          | `.env` + `.gitignore`, no key in source |
| R10 Documentation     | this README                            |

## Stretch goals (optional)

Finished early, or want more of a challenge? Pick one of these. Each pushes past
what Lab 1 covered and touches a different part of the design.

### S1 — Handle "context too long" as its own error

**Goal:** teach the assistant to recognise when a request is too large for the
model and tell the user what to do about it, instead of showing a generic error.

**Why it matters:** not every failure is the same. A too long request will fail
again no matter how many times you retry, so it is a terminal error, and the
user needs a different message from "the service is busy".

**What to build:**

1. In `llm.py`, add a `ContextLengthError` (a terminal error, like `InvalidRequestError`) with a `user_message` that suggests clearing history or lowering `--max-tokens`.
2. Extend `_classify_error()` so a context length failure maps to it. Match on the class name and on message text such as "context length" or "maximum context".
3. Make sure the retry loop treats it as terminal, so it is never retried.
4. In `main.py`, when this error is raised, roll back the unanswered user message the same way other errors do.

**Done when:** sending a very long prompt (paste a large block of text, or set a
tiny model context) prints your friendly message once, with no retries, and the
conversation history stays clean.

### S2 — Save and resume a conversation

**Goal:** add `/save <name>` and `/load <name>` commands so a chat can be kept
between runs.

**Why it matters:** the conversation is just data, a list of role and content
messages. Once you see that, persisting it is a small step, and it makes the
memory idea from R5 concrete.

The reference implementation stores conversations in a local SQLite database
(`conversations.db`) instead of JSON files, using the standard library
`sqlite3` module in `store.py`. It also resumes automatically: on startup, if
anything was ever saved, the most recently saved conversation is loaded back
into the session, so you can pick up where you left off without a command.
`/load` still lets you choose a specific saved conversation by name.

That keeps persistence behind one small
module with no new dependency, and `main.py` stays concerned only with user
interaction.

**What to build:**

1. In `store.py`, wrap a `sqlite3` database that keeps conversations by name.
2. In `main.py`, add `/save <name>` that writes `self.messages` under that name.
3. Add `/load <name>` that reads the conversation back into `self.messages`, replacing the current history.
4. Validate what is loaded: it should be a list of dicts that each have a `role` and `content`. On a bad entry, print a friendly message and keep the current conversation.
5. Update `/help` and the README command list to include the two new commands.

**Done when:** you can hold a short chat, run `/save mychat`, quit, start a
fresh session, run `/load mychat`, and the assistant answers the next
question with the earlier context in mind. The conversation survives the
restart and lives in `conversations.db`.

Add a short note in `NOTES.md` about which stretch goal you did and what you
learned from it.

## Reflection questions

_Answer these here as part of your submission._

1. **What happens when temperature is changed from 0.2 to 1.0?**

2. **Why should an application not retry every API error?**

3. **Why should the API key not be stored directly in the source code?**

4. **Why does conversation history increase token usage?**

5. **What is the main advantage of streaming?**

6. **If 10,000 users use your application, what engineering problems might appear?**
