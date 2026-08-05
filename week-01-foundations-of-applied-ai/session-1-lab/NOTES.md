# Lab notes

*Fill this in as you go — it's part of your submission (Lab 0).*

## Statelessness
What happened when you sent only the latest message vs. the full history?

Each `--once` call sends a single message with no history, so the model has no memory between calls. I said "Hi! My name is Alex." and then in a separate call asked "What is my name?" — the bot replied it didn't know, because the first message was never sent again. The API is stateless: every request is independent.

In the interactive `chat_loop` the full history (system + all prior user/assistant messages) is sent with every request, so the same follow-up question was answered correctly: "Your name is Alex!" — the model only "remembers" what is included in the request.

## Temperature
How did `--temp 0.2` compare to `--temp 1.3` on the same prompt?

I asked the same prompt ("Write a one-line slogan for a coffee shop app.") three times at each temperature:

- `--temp 0.2`: very stable, near-identical output each time ("Your daily brew, just a tap away." / "Your perfect brew, just a tap away."), small wording variations only.
- `--temp 1.3`: more variety — a different phrase each run ("Your next favorite coffee is just a tap away."). Answers were still coherent, but the bot was more willing to pick different words and structures.

Low temperature = more deterministic/consistent; high temperature = more random/creative.

## Tokens
What did you notice about token counts as prompts got longer?

I compared a short prompt ("What is the capital of France?") against a long, detailed one. The short prompt used ~90 prompt tokens / 102 total; the longer prompt used ~144 prompt tokens but ~1630 completion tokens (~1774 total). Two observations:

- Input (prompt) tokens grow with prompt length, so sending full conversation history makes each call more expensive.
- Longer prompts also tend to produce longer, more detailed replies, so completion tokens can grow much faster than the prompt itself — total token cost roughly tracked the size of the answer.

## Anything that surprised you or broke

- The bot initially failed with a 401 — the `.env` file in `week-01-foundations-of-applied-ai/` was overwritten with a placeholder key (18-char "your-..." value). Replacing it with a real key fixed it.
- The base URL is `https://opencode.ai/zen/v1`, and the model ID there is `deepseek-v4-flash-free`, not `deepseek/deepseek-v4-flash:free` (which returned "Model ... is not supported"). The default in `.env.example` was built for Groq, so the model name had to be corrected for this endpoint.
- `load_dotenv()` finds `.env` in the parent directory of the lab folder, which is easy to miss when looking for configuration.
- `python` is not installed on this Mac — only `python3`.
