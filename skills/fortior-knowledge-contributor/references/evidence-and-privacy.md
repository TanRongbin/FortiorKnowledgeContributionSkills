# Evidence & Privacy

## Evidence preference

Prefer, roughly in this order:

1. reproducible test or controlled A/B result
2. proven code path / diff
3. commit
4. log / waveform / trace
5. engineering document
6. explicit user confirmation
7. inference

Evidence quality determines confidence; absence of evidence must lower confidence rather than trigger invention.

## Proprietary source code

Prefer storing references and summaries instead of complete files:

- repository identifier only if user allows it
- branch/commit only if user allows it
- relative file path only if user allows it
- minimal relevant code excerpt only if user allows it
- technical explanation of the change

Review metadata such as project/product name, chip model, engineering series, CPU architecture, module name and code symbols can also reveal proprietary context. Populate them from reliable evidence, but do not reconstruct or expose source identity that conflicts with the user's publication/disclosure choices.

## Never submit

- Feishu App Secret or access tokens
- API keys/passwords
- SSH/TLS/private signing keys
- customer credentials
- unrelated personal information
- large proprietary code dumps

## Publication boundary

`visibility` and disclosure booleans are user decisions. AI may recommend safer defaults, but may not silently broaden permission.
