# Compétence : diagnostiquer un endpoint IBM PA

Protocole de diagnostic quand un endpoint IBM PA retourne des données
inattendues, une erreur, ou des valeurs null inexpliquées.

→ Référence IBM PA complète : `docs/learning/ibm_pa.md`

---

## Étape 1 : Appel direct sans cache

Vérifier que le problème vient bien d'IBM PA et non du cache ou du mapping :

```bash
curl -u "apikey:<IBM_PA_API_KEY>" \
  "<IBM_PA_BASE_URL>/api/<TENANT_ID>/v0/tm1/<endpoint>"
```

- Si l'appel direct échoue → problème IBM PA ou authentification
- Si l'appel direct réussit → problème dans le mapping ou le cache

---

## Étape 2 : Consulter `$metadata`

Avant de déboguer un mapping, vérifier le schéma réel du tenant :

```bash
curl -u "apikey:<IBM_PA_API_KEY>" \
  "<IBM_PA_BASE_URL>/api/<TENANT_ID>/v0/tm1/$metadata"
```

Le document CSDL retourné décrit les champs **réellement disponibles** sur
ce tenant. La doc statique IBM peut diverger du comportement SaaS réel (constaté S2).

---

## Étape 3 : Inspecter `raw_data`

Appeler l'endpoint avec `include_raw=true` :

```
GET /api/v1/servers?include_raw=true
```

Comparer `raw_data` avec le mapping dans `_refresh_from_ibm_pa` du service.
Un champ null en sortie mappée est souvent un champ absent du payload brut.

---

## Étape 4 : Méthode cas qui marche / cas qui plante

Identifier deux appels : un qui produit le résultat attendu, un qui ne le
produit pas. Comparer les paramètres, les réponses brutes, le parcours dans
le code. La divergence révèle la cause.

**Exemple vécu (S2)** : `force_refresh=true` fonctionnait, `force_refresh=false`
retournait 500. Cause : datetime naive SQLite comparé à un datetime aware UTC.

---

## Règle d'authentification

L'appel curl doit toujours utiliser `apikey` comme username, jamais l'email :

```bash
curl -u "apikey:<IBM_PA_API_KEY>" ...    # correct
curl -u "email@exemple.com:<clé>" ...   # faux → 401/403
```

→ Règle complète : `.claude/rules/ibm-pa-auth.md`

---

## Référence

- `docs/learning/ibm_pa.md` — endpoints découverts, pièges, sources IBM officielles
- `.claude/rules/ibm-pa-auth.md` — règle d'authentification
- `docs/learning/decisions.md` D-004 — décision sur l'auth IBM PA
