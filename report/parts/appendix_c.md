## Appendix C Extra tables

| Model | Threshold (median score of reliable band) | E1 Spearman rho | E1 parse failures |
|---|---|---|---|
| qwen3.5-397b | {{llm.per_model.qwen3.5-397b.threshold|.2f}} | {{llm.per_model.qwen3.5-397b.E1_rho.rho|.2f}} | {{llm.per_model.qwen3.5-397b.E1_parse_fail}} |
| deepseek-v4-flash | {{llm.per_model.deepseek-v4-flash.threshold|.2f}} | {{llm.per_model.deepseek-v4-flash.E1_rho.rho|.2f}} | {{llm.per_model.deepseek-v4-flash.E1_parse_fail}} |
| glm-5.2 | {{llm.per_model.glm-5.2.threshold|.2f}} | {{llm.per_model.glm-5.2.E1_rho.rho|.2f}} | {{llm.per_model.glm-5.2.E1_parse_fail}} |
| gemma-4-31b-it | {{llm.per_model.gemma-4-31b-it.threshold|.2f}} | {{llm.per_model.gemma-4-31b-it.E1_rho.rho|.2f}} | {{llm.per_model.gemma-4-31b-it.E1_parse_fail}} |

*Table C1. Per-model validity (real model measurements). Thresholds at the 0.6 and 0.8 reliable bands are in `results/analysis.json`.*

| Model | Honest page, no policy: crossed | Honest page with policy: crossed |
|---|---|---|
| qwen3.5-397b | {{llm.summary.E3h.qwen3.5-397b.honest_base.rate|.0%}} | {{llm.summary.E3h.qwen3.5-397b.honest_policy.rate|.0%}} |
| deepseek-v4-flash | {{llm.summary.E3h.deepseek-v4-flash.honest_base.rate|.0%}} | {{llm.summary.E3h.deepseek-v4-flash.honest_policy.rate|.0%}} |
| glm-5.2 | {{llm.summary.E3h.glm-5.2.honest_base.rate|.0%}} | {{llm.summary.E3h.glm-5.2.honest_policy.rate|.0%}} |
| gemma-4-31b-it | {{llm.summary.E3h.gemma-4-31b-it.honest_base.rate|.0%}} | {{llm.summary.E3h.gemma-4-31b-it.honest_policy.rate|.0%}} |

*Table C2. Honest newcomer pages (E3h, 40 outlets per model, real model measurements).*

| Second provider | Threshold | Spearman rho (n=100) | Control crossed | Boilerplate crossed | Injection crossed | Combined crossed |
|---|---|---|---|---|---|---|
| gemini:gemma-4-31b-it | {{robust.gemini:gemma-4-31b-it.threshold|.2f}} | {{robust.gemini:gemma-4-31b-it.rho|.2f}} | {{robust.gemini:gemma-4-31b-it.E3.control.crossed}} of 30 | {{robust.gemini:gemma-4-31b-it.E3.A3_boilerplate.crossed}} of 30 | {{robust.gemini:gemma-4-31b-it.E3.A5_injection.crossed}} of 30 | {{robust.gemini:gemma-4-31b-it.E3.combined.crossed}} of 30 |
| groq:openai/gpt-oss-120b | {{robust.groq:openai/gpt-oss-120b.threshold|.2f}} | {{robust.groq:openai/gpt-oss-120b.rho|.2f}} | {{robust.groq:openai/gpt-oss-120b.E3.control.crossed}} of 30 | {{robust.groq:openai/gpt-oss-120b.E3.A3_boilerplate.crossed}} of 30 | {{robust.groq:openai/gpt-oss-120b.E3.A5_injection.crossed}} of 30 | {{robust.groq:openai/gpt-oss-120b.E3.combined.crossed}} of 30 |

*Table C3. Second-provider robustness subsets (real model measurements, descriptive only, not part of any hypothesis test).*

Simulation sensitivity (T6 informed-source noise 0.05 and 0.12 against the base 0.10), the second-provider robustness subsets and the full disagreement list between the two auditability coders are in `results/sims/t6sens.json`, `results/main/R1*`, and `results/analysis.json` respectively. With an informed source noise of 0.12 an honest informed newcomer usually did not cross T6b within 500 claims.

