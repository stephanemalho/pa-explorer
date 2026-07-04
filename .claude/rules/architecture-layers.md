---
paths:
  - "app/**"
---

# Règle : architecture en couches

Pattern obligatoire : `client → service → router`.

- Toute logique métier vit dans `app/services/` — jamais dans les routers
- Tout appel HTTP vers IBM PA passe par `app/clients/ibm_pa.py` — jamais dans `routers/` ni `services/`
- Toute injection de dépendance utilise `Depends()` — jamais instanciée manuellement dans un router

Exception documentée **D-014** : `validate_ibm_pa_credentials` dans `AuthService` instancie
`IBMPAClient` directement car la validation précède toute session utilisateur (contexte pré-auth,
pas de credentials en base au moment de l'appel).
