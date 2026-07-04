# Règle : IBM PA Basic Auth

## Champ d'application

- `app/clients/**`

## Règle

Le username IBM PA Basic Auth est toujours la chaîne littérale `"apikey"` — jamais l'email utilisateur.

```python
httpx.BasicAuth("apikey", api_key)   # correct
httpx.BasicAuth(user_email, api_key) # faux -> AuthorizedConnectionFailed immédiat
```

Source : D-004 dans `docs/learning/decisions.md`.
