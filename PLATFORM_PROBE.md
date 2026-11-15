# PLATFORM_PROBE

Run 2026-11-15 09:56 UTC. One tiny call per candidate model.

| Model | Status | HTTP | Latency s | Output item types | Usage | Parsed |
|---|---|---|---|---|---|---|
| qwen3.5-397b | ok | 200 | 20.07 | ['reasoning', 'message'] | {"input_tokens": 122, "input_tokens_details": {"audio_tokens": null, "cached_tokens": 0, "cached_tokens_details": null, "image_tokens": null, "text_tokens": null, "video_tokens": null, "cache_write_tokens": 0, "input_tokens_per_turn": [], "cached_tokens_per_turn": []}, "output_tokens": 1571, "output_tokens_details": {"audio_tokens": null, "reasoning_tokens": 1529, "text_tokens": null, "tool_output_tokens": 0, "output_tokens_per_turn": [], "tool_output_tokens_per_turn": []}, "total_tokens": 1693, "cost": 0.0055655999999999995} | json |
| deepseek-v4-flash | ok | 200 | 1.19 | ['reasoning', 'message'] | {"input_tokens": 186, "input_tokens_details": {"audio_tokens": null, "cached_tokens": 0, "cached_tokens_details": null, "image_tokens": null, "text_tokens": null, "video_tokens": null, "cache_write_tokens": 0, "input_tokens_per_turn": [], "cached_tokens_per_turn": []}, "output_tokens": 90, "output_tokens_details": {"audio_tokens": null, "reasoning_tokens": 48, "text_tokens": null, "tool_output_tokens": 0, "output_tokens_per_turn": [], "tool_output_tokens_per_turn": []}, "total_tokens": 276, "cost": 2.026464e-05} | json |
| glm-5.2 | ok | 200 | 3.47 | ['reasoning', 'message'] | {"input_tokens": 117, "input_tokens_details": {"audio_tokens": null, "cached_tokens": 0, "cached_tokens_details": null, "image_tokens": null, "text_tokens": null, "video_tokens": null, "cache_write_tokens": 64, "input_tokens_per_turn": [], "cached_tokens_per_turn": []}, "output_tokens": 124, "output_tokens_details": {"audio_tokens": null, "reasoning_tokens": 87, "text_tokens": null, "tool_output_tokens": 0, "output_tokens_per_turn": [], "tool_output_tokens_per_turn": []}, "total_tokens": 241, "cost": 0.0007094} | json |
| gemma-4-31b-it | ok | 200 | 0.75 | ['message'] | {"input_tokens": 123, "input_tokens_details": {"audio_tokens": null, "cached_tokens": 0, "cached_tokens_details": null, "image_tokens": null, "text_tokens": null, "video_tokens": null, "cache_write_tokens": 0, "input_tokens_per_turn": [], "cached_tokens_per_turn": []}, "output_tokens": 35, "output_tokens_details": {"audio_tokens": null, "reasoning_tokens": 0, "text_tokens": null, "tool_output_tokens": 0, "output_tokens_per_turn": [], "tool_output_tokens_per_turn": []}, "total_tokens": 158, "cost": 2.297e-05} | json |

Working models: ['qwen3.5-397b', 'deepseek-v4-flash', 'glm-5.2', 'gemma-4-31b-it']

Adaptive Data: see SDK_SURFACE.md.
