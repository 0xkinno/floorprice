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

## Not used, so not claimed
- Adaptive Data (dataset create and evaluate). The docs describe dataset-level before and after quality scores on a 0 to 10 scale.
  A per-row score is not stated. T8 is therefore not run. If the probe finds a per-row score, this file is amended and T8 is added under A3 and A4.
