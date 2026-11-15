# SDK_SURFACE (what the Adaption surface offers, and what we use)

Read from the public docs on 2026-11-15 (https://docs.adaptionlabs.ai). Live behaviour is confirmed by `scripts/probe.py`
once an API key is present; until then PLATFORM_PROBE.md does not exist and nothing below counts as measured.

## Used
- Responses API: `POST https://api.prod.adaptionlabs.ai/api/v1/responses`, bearer key. Request fields used: model, instructions, input, temperature, max_output_tokens.
  Read only `output[]` items of type message and their `output_text` content. Reasoning items are skipped.
- Hosted models in the docs: gemma-4-31b-it, glm-5.2, qwen3.5-397b, gemma-4-26b-a4b-it, qwen3.8-27b, deepseek-v4-flash, glm-53-flash.
  Candidates for this study: qwen3.5-397b, deepseek-v4-flash, glm-5.2, gemma-4-31b-it (four families). "Model availability can vary by API key."
- Prices are in credits per million tokens (input, output): gemma-4-31b-it 0.09/0.34; glm-5.2 1.40/4.40; qwen3.5-397b 0.55/3.50; deepseek-v4-flash 0.045/0.14.
  The docs do not state a dollar value per credit.

## Measured by scripts/probe.py on 2026-11-15 (see PLATFORM_PROBE.md and results/probe.json)
- All four candidate models answered with HTTP 200 and parsed as strict JSON: qwen3.5-397b, deepseek-v4-flash, glm-5.2, gemma-4-31b-it.
- Output items: reasoning plus message for qwen, deepseek and glm; message only for gemma. Reading only the message item is required.
- The response `usage` object carries a `cost` field. It equals the published credit prices applied to the token counts, so it is in credits.
  One probe call cost 0.0056 credits for qwen3.5-397b (1,571 output tokens, most of them reasoning) and about 0.00002 for gemma and deepseek.
- Latency: qwen3.5-397b about 20 s (reasoning), glm-5.2 about 3.5 s, deepseek-v4-flash about 1.2 s, gemma-4-31b-it under 1 s.
- Rate limit: about 25 requests per minute for the key, shared across models. The 26th request in a window returns HTTP 429 with `Retry-After: 60`.
  The runner uses one global request pace (2.6 s) and honours Retry-After.

## Not used, so not claimed
- Adaptive Data (dataset create and evaluate). The docs describe dataset-level before and after quality scores on a 0 to 10 scale.
  A per-row score is not stated. T8 is therefore not run. If the probe finds a per-row score, this file is amended and T8 is added under A3 and A4.
