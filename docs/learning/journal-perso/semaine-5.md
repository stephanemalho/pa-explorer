# Semaine 5 — Feedback Loops et tests

La semaine 5 marque un changement de nature dans le parcours. Les semaines 
précédentes ajoutaient des fonctionnalités visibles. La semaine 5 construit 
l'infrastructure de qualité qui rend le code fiable et permet à Claude Code 
de travailler avec plus d'autonomie. C'est une semaine de qualité plutôt que 
de fonctionnalité, mais elle est fondamentale pour tout ce qui suit.

L'apprentissage central de la semaine est double. D'une part la philosophie 
des feedback loops, c'est-à-dire les mécanismes qui disent rapidement si le 
code fonctionne. D'autre part la maîtrise pratique des tests pytest avec trois 
techniques de mock distinctes.

---

## La philosophie des feedback loops

La question fondatrice de la semaine est "le code est-il bon marché ?". Si 
Claude Code produit du code rapidement et à faible coût, alors la ressource 
rare n'est plus le code mais le temps humain de validation. Les feedback loops 
automatisent cette validation pour libérer ce temps.

Trois feedback loops structurent un projet Python. Les tests automatisés via 
pytest qui disent en quelques secondes si le code est cassé. Le formatage et 
le linting automatiques qui maintiennent la cohérence. Les pre-commit hooks 
qui bloquent le commit de code défaillant. Cette semaine a posé le premier 
de ces trois piliers, les tests, et préparé le terrain pour les deux autres.

---

## Le skill do_work, première brique de la semaine

Avant d'écrire le moindre test, j'ai créé un skill de qualité transversal, 
do_work, dans docs/skills/do_work.md. Ce skill formalise les vérifications à 
effectuer avant de signaler la complétion d'une tâche.

La conception de ce skill a suivi une démarche structurée. J'ai d'abord demandé 
à Claude Code une analyse préparatoire qui recensait les pièges récurrents du 
parcours, les conventions strictes du projet, et les actions mécaniques 
automatisables. À partir de cette matière, le skill a été rédigé avec une 
distinction clé entre vérifications bloquantes et vérifications indicatives.

Les sept vérifications bloquantes couvrent le pattern client service router, 
la normalisation UTC des datetimes, l'absence d'async def, la cohérence modèle 
schéma réponse, l'authentification IBM PA, l'installation des dépendances, et 
le passage des tests. Les six vérifications indicatives couvrent des points 
recommandés mais non bloquants.

Le skill a fait ses preuves dès sa première application réelle. Il a détecté 
une violation architecturale pré-existante dans auth_service.py, l'instanciation 
directe d'IBMPAClient dans validate_ibm_pa_credentials. Cette détection a donné 
lieu à la décision D-014 qui documente cette instanciation comme une exception 
reconnue, justifiée par le contexte de pré-authentification.

Apprentissage important sur le skill. Un bon skill de qualité ne traite pas 
tout au même niveau. La distinction bloquant versus indicatif évite que Claude 
Code soit ralenti par des vérifications mineures tout en garantissant que les 
points critiques sont toujours respectés.

---

## L'infrastructure pytest et les premiers tests

La mise en place de pytest a commencé par les tests les plus simples pour 
valider l'outillage. Les tests de l'endpoint health, sans aucune dépendance 
externe, et les tests du module de chiffrement Fernet, purs et sans dépendance.

Le test de non-déterminisme du chiffrement mérite une mention. Il vérifie que 
chiffrer la même chaîne deux fois donne deux résultats différents, grâce au 
nonce aléatoire de Fernet. C'est un test qui valide une vraie propriété de 
sécurité, pas juste un fonctionnement basique. Si le chiffrement était 
déterministe, un attaquant ayant accès à la base pourrait déduire que deux 
utilisateurs ont les mêmes credentials.

Un piège technique a été résolu lors de la mise en place. Les singletons 
settings et _fernet sont créés à l'import des modules applicatifs. Le conftest 
positionne donc des variables d'environnement de repli via os.environ.setdefault 
avant tout import, sans écraser un .env.local existant.

---

## Les trois techniques de mock, cœur de l'apprentissage

L'apprentissage le plus précieux de la semaine est la maîtrise de trois 
techniques de mock distinctes, chacune adaptée à une situation.

### Technique un, la fausse classe explicite

Pour tester un service qui reçoit son client par injection via le constructeur, 
on écrit une fausse classe FakeIBMPAClient dans tests/fakes.py. Cette classe 
implémente les mêmes méthodes que le vrai client mais retourne des données 
fixes. Elle s'applique à ServerService, CubeService et DimensionService.

Leçon clé apprise ici. Un mock doit respecter le contrat de la méthode qu'il 
remplace, pas celui de l'API sous-jacente. Comme le vrai get_servers fait 
return data.get("value", []) et retourne donc une liste directe, le faux client 
doit aussi retourner une liste directe, pas l'enveloppe OData complète. J'ai 
confirmé ce point en inspectant le code réel du client.

La fausse classe a été enrichie progressivement. D'abord pour ServerService 
avec un compteur d'appels permettant de distinguer cache hit et cache miss. 
Puis pour CubeService et DimensionService avec des méthodes paramétrées et la 
mémorisation des derniers paramètres reçus, ce qui permet de vérifier que le 
service transmet bien le bon nom de serveur ou de cube au client.

### Technique deux, le patch

Pour tester du code qui instancie son client en interne, sans point d'injection, 
on utilise unittest.mock.patch. C'est le cas de validate_ibm_pa_credentials qui, 
à cause de la décision D-014, crée IBMPAClient elle-même. Le patch remplace 
temporairement la classe IBMPAClient là où elle est utilisée, dans le module 
auth_service, de sorte que même l'instanciation interne utilise le faux.

Leçon clé apprise ici. On patche l'objet là où il est utilisé, pas là où il 
est défini. Et la distinction entre return_value pour simuler un retour normal 
et side_effect pour simuler une exception est fondamentale.

Cette technique a aussi révélé un lien profond entre architecture et 
testabilité. Le choix D-014 d'instancier le client en interne a pour 
conséquence directe l'obligation d'utiliser patch plutôt que la fausse classe. 
Un code conçu pour l'injection est plus simple à tester.

### Technique trois, dependency_overrides

Pour tester un endpoint HTTP complet via TestClient, on utilise le mécanisme 
dependency_overrides de FastAPI. Il permet de remplacer une dépendance réelle 
par une version de test pour la durée des tests. La fixture client override 
get_db pour utiliser une base SQLite en mémoire isolée.

Un détail technique important a été anticipé dans l'infrastructure. Le 
StaticPool avec check_same_thread à False garantit que TestClient et la base 
partagent le même moteur en mémoire malgré l'exécution potentielle dans des 
threads différents.

Pour les tests d'endpoint d'authentification, les deux techniques se combinent. 
Le dependency_overrides gère la base, et le patch gère la validation IBM PA. 
Chaque mécanisme pour ce qu'il fait de mieux.

---

## La couverture finale des tests

À la fin de la partie test de la semaine 5, le projet compte cinquante-et-un 
tests répartis sur trois niveaux.

Le niveau unitaire pur avec le chiffrement. Le niveau service avec la logique 
de cache des trois services métier et la couverture complète d'AuthService 
incluant l'allowlist, les magic links, les sessions et la validation des 
credentials. Le niveau endpoint HTTP avec les deux routes d'authentification, 
le pattern de non-divulgation, et la gestion des cookies de session.

Les tests s'exécutent en environ un dixième de seconde. C'est le bénéfice 
concret des feedback loops. Une vérification qui prenait plusieurs minutes en 
manuel via Swagger est maintenant instantanée et reproductible.

Le piège du datetime naïf de SQLite, déjà rencontré en semaines 2 et 4, s'est 
manifesté à nouveau pendant l'écriture des tests d'AuthService, quand 
db_session.refresh retourne un datetime sans timezone. La normalisation via 
replace tzinfo timezone utc reste le pattern de résolution. C'est la 
confirmation que le piège B-2 du skill do_work documente un problème réel et 
récurrent.

---

## Pour la suite

Alembic a depuis été installé pour gérer les migrations de schéma proprement, 
ce qui remplace la suppression manuelle de pa_explorer.db à chaque modification 
de modèle. La migration initiale `5e9bf0f2db8c` est appliquée (head), le seed a 
été déplacé dans `scripts/seed_db.py`, et la règle canonique 
`docs/agent-rules/alembic-schema.md` acte qu'Alembic est l'unique propriétaire 
du schéma. Cette étape clôture la semaine 5.

Plusieurs sujets ont été identifiés mais reportés. Les tests des dépendances 
de sécurité get_current_user et get_ibm_pa_client_for_user. L'outillage ruff 
pour le formatage et le linting. Les pre-commit hooks. L'envoi du magic link 
par email réel via Mailtrap. L'endpoint logout. La résorption de la dette 
technique D-010 sur l'atomicité transactionnelle de verify_magic_link.

Ces reports sont des choix assumés pour ne pas tomber dans la sur-couverture 
et garder le cap sur les apprentissages structurants de chaque semaine.

Points de sécurité à adresser avant mise en production :

- Stratégie de rotation de la clé Fernet à documenter (perte de la clé = base illisible)
- Stratégie de backup chiffré de la base SQLite
- Cookie de session : `secure=True` à activer dès le déploiement en HTTPS
- Investiguer HashiCorp Vault ou équivalent pour la gestion des secrets en production
