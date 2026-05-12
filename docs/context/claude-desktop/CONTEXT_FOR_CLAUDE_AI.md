# Contexte pour Claude AI assistant pédagogique

Ce fichier sert à remettre Claude AI dans le contexte de mon parcours 
d'apprentissage Claude Code et de mon projet PA-Explorer au début d'une 
nouvelle conversation. Je le copie-colle en début de session avec un 
message qui dit:

"Voici le contexte de notre travail ensemble, lis-le 
attentivement avant de me répondre, puis on continue".

---

## Le projet PA-Explorer

PA-Explorer est un POC backend pour IBM Planning Analytics on Cloud, 
développé en Python avec FastAPI et SQLAlchemy. Il consomme l'API REST 
TM1 d'IBM PA pour exposer des serveurs, cubes, dimensions et données 
de cellules à un futur frontend BI assisté par IA.

L'environnement de développement est sur ma machine Windows avec un 
tenant de démo IBM PA hébergé sur eu-central-1.planninganalytics.saas.ibm.com. 
J'ai un siège Team chez Anthropic et le feu vert de mon entreprise pour 
ce POC.

La vision long terme est un outil de monitoring de performance pour 
analystes business. L'utilisateur sélectionne un serveur TM1 (par 
exemple Seminaire), navigue dans les cubes (par exemple Ventes), filtre 
par zone ou pays, saisit des chiffres comme coûts, ventes, chiffre 
d'affaires, et compare horizontalement avec l'historique et 
verticalement avec les autres produits. Un agent IA doit analyser 
les anomalies et bonnes performances, et alerter sur les écarts 
inattendus par rapport au forecast.

L'aspect novateur est que ce POC peut servir de démonstration interne 
pour l'intégration de Git et GitHub dans le workflow de gestion d'actifs 
TM1, sujet auquel mon équipe commence à s'intéresser.

## Mon profil d'apprentissage

Je suis développeur confirmé sur plusieurs langages avec des projets 
conséquents derrière moi. Je suis débutant sur Python et FastAPI mais 
j'apprends vite par analogie avec JavaScript et l'écosystème Node.

Je dispose de quatre à six heures par semaine pour ce projet, à un 
rythme régulier sur huit semaines.

Mon objectif principal est de monter en compétence sur l'utilisation 
avancée de Claude et Claude Code, avec le POC IBM PA comme support 
d'apprentissage et livrable professionnel pour mon équipe.

## Le programme d'apprentissage

Le parcours suit une adaptation du programme AIhero "Claude Code for 
Real Engineers", étalé sur huit semaines. Le détail complet est dans 
docs/learning/README.md.

[À METTRE À JOUR À LA FIN DE CHAQUE SEMAINE]

État actuel : Semaine 2 terminée le 28 avril 2026.

Semaine 1 accomplie. Mise en place du projet, premier endpoint health, 
configuration de base SQLite, gestion des credentials par env files.

Semaine 2 accomplie. Feature complète de listing des serveurs TM1 avec 
authentification IBM PA SaaS via apikey, client httpx, pattern cache 
aside avec TTL configurable, gestion d'erreurs en sept types d'exceptions 
métier, exposition de routes GET et POST avec Swagger.

Semaine 3 accomplie. Création du CLAUDE.md consolidé en français à 
la racine du projet pour le steering automatique de Claude Code. 
Création du skill add_ibm_pa_endpoint.md dans docs/skills qui 
formalise la procédure d'ajout d'un endpoint IBM PA. Application 
concrète sur list_cubes qui expose maintenant la liste des cubes 
TM1 par serveur. Découverte de la richesse réelle des cubes IBM PA 
avec règles de calcul, feeders et attributs. Découverte d'un piège 
Python sur str.format qui ne fait pas de format partiel, contourné 
par généralisation de la méthode _url du client. Test de validation 
du steering effectué sur list_dimensions, qui a confirmé que Claude 
Code consulte bien les fichiers de référence et applique les patterns 
documentés.

## Mode de travail établi entre nous

Tu composes les prompts pour Claude Code avec une note pédagogique 
au-dessus qui explique la logique du prompt. Je copie ces prompts 
dans Claude Code et j'observe l'exécution.

Sur les décisions architecturales importantes, tu me poses des 
questions plutôt que de décider seul, parce que je suis le seul à 
connaître mon métier et mes utilisateurs cibles.

Je tiens un journal d'apprentissage dans docs/learning/ que je 
maintiens à jour à la fin de chaque session.

Sur deux ou trois moments charnières du programme, notamment la 
semaine 3 sur le steering et la semaine 5 sur les feedback loops, 
tu me feras composer un ou deux prompts moi-même pour pratiquer 
sans en faire mon sujet quotidien.

## Décisions architecturales clés

Le détail complet est dans docs/learning/decisions.md. En résumé :

Stack Python 3.12 avec FastAPI, SQLAlchemy synchrone, httpx pour les 
appels API distants, pytest et pytest-asyncio prêts pour la semaine 5.

Cache à deux niveaux. SQLite via SQLAlchemy pour les métadonnées 
relationnelles, Parquet à venir pour les données de cellules 
volumineuses.

Authentification IBM PA SaaS via Basic Auth avec username "apikey" 
littéral et clé API en password.

Gestion des erreurs en hiérarchie d'exceptions métier IBMPAError, 
mappées vers des codes HTTP cohérents 502 503 504 par le router.

TTL de cache à 300 secondes en développement, à remonter en production. 
Stratégie de rafraîchissement à trois couches.

Erreur stricte 503/504 si IBM PA est indisponible et cache expiré, à 
revoir vers cache dégradé avec flag stale quand le frontend saura 
afficher cet état visuellement.

Champ raw_data en JSON brut conservé sur le modèle pour absorber les 
évolutions IBM PA sans migration et fournir la matière aux LLMs.

## Particularités à retenir

Je travaille sur Windows avec PowerShell, donc certaines commandes 
Unix doivent être adaptées. La procédure complète de réinitialisation 
de la base SQLite est documentée dans le README à la racine du projet.

Les logs uvicorn ne s'affichent parfois pas dans le terminal Windows 
PowerShell, ce qui complique le débogage. La parade actuelle est de 
faire des tests directs en navigateur ou via curl, et de copier les 
réponses pour analyse.

Migration vers Alembic à prévoir en semaine 5 ou 6 pour gérer les 
évolutions de schéma SQLAlchemy sans suppression de la base.

## Pour démarrer une nouvelle session avec moi

Copie-colle le contenu complet de ce fichier en début de message, 
puis ajoute ta question ou ta demande. Je lirai le contexte 
attentivement et je reprendrai notre travail là où on s'était arrêtés.