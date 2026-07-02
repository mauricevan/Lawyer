# Vendor and model risk review (plan9 V)

**Cadence:** kwartaal + bij provider-wijziging  
**Owner:** backend

## LLM providers

| Provider | Use | Risk | Mitigation |
|---|---|---|---|
| OpenRouter | Primary generation | API outage, rate limits | `LLM_PROVIDER` switch, fallback text |
| Anthropic | Alternate | Key exposure, cost | Secrets in env only, pip-audit |

## Embedding / reranker

| Component | Model | Risk | Mitigation |
|---|---|---|---|
| Embeddings | multilingual-e5-large | HF hub down | Cached weights in image/volume |
| Reranker | cross-encoder | Latency spike | Budget + top-k cap |

## Review checklist

- [ ] API keys rotated per policy
- [ ] `pip-audit` / dependency scan groen
- [ ] Fallback path getest (LLM failure → structured fallback)
- [ ] Cost/latency binnen portfolio targets
- [ ] Update [strategic-risk-register.yaml](./strategic-risk-register.yaml) scores

## Escalatie

Exposure ≥ 12 → architecture review + mogelijke ADR
