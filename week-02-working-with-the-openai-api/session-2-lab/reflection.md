# Reflection

Practical AI for Software Engineering · Week 2 · Lab 2

**1. What happens when temperature is changed from 0.2 to 1.0?**

The model's output becomes more random. At 0.2 the model picks near-top
tokens, so answers are focused and repeatable. At 1.0 the probability
distribution is flatter, so you get more varied, creative, sometimes wilder
wording and, for coding tasks, a higher chance of irrelevant or wrong
details. You can change it live with `/temperature 1.0`.

**2. Why should an application not retry every API error?**

Retrying is only useful for transient failures (rate limits, timeouts,
server outages) where the next attempt may succeed. Errors like a bad API
key, an invalid model, or a malformed request will fail identically every
time, so retrying just wastes time and tokens, and hammers the API. That is
why `llm.py` splits errors into terminal (`ConfigurationError`,
`InvalidRequestError`), which are never retried, and transient
(`RateLimitError`, `ServiceUnavailableError`), which use backoff up to
`config.MAX_RETRIES`.

**3. Why should the API key not be stored directly in the source code?**

The key is a secret that grants access and bills anyone who has it. If it is
hard-coded, it gets committed to git, ends up in your history forever, and
leaks when the repo is shared or pushed to a public host. Keeping it in
`.env` (git-ignored via `.gitignore`) or an environment variable means the
secret stays out of the code, out of the repo, and can be rotated without
editing source. This is requirement R9.

**4. Why does conversation history increase token usage?**

The API is stateless, so every turn resends the entire `messages` list
(system prompt plus all prior user/assistant turns). Each new exchange
grows the history, so every request costs input tokens for every previous
message, not just the newest one. The usage line printed after each reply
shows this: the longer your chat, the larger the `input` token count
becomes, and eventually a long history can also exceed the model's context
window.

**5. What is the main advantage of streaming?**

Perceived speed. The first tokens appear almost immediately instead of
waiting for the whole reply, which makes long answers feel faster and gives
the user feedback that the model is working. In `main.py`,
`_stream_reply()` prints each chunk as it arrives from `service.stream()`
instead of blocking until the full response is done.

**6. If 10,000 users use your application, what engineering problems might
appear?**

- Rate limits: a single API key throttles quickly; you need quotas,
  queuing, or pooled keys, and retry backoff.
- Cost: token usage scales per request, so tracking (`total_usage`) and
  caching matter.
- Latency and concurrency: a single Python process serializes requests, so
  you need async or multiple workers/replicas.
- Resource exhaustion: memory and CPU per session grow with conversation
  history, requiring cleanup and limits.
- Secret management: a leaked key has a bigger blast radius, so store keys
  server-side and never in the client.
