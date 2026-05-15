## Points à ne pas négligé pour la suite du projet :

### Authentification

- Premier point sur la validation de l'email. Le schéma AuthRequest utilise un str simple pour l'email avec un TODO de migration vers EmailStr en phase 2. Cela signifie qu'aujourd'hui le système accepterait n'importe quelle chaîne comme email, y compris des chaînes invalides. Ce n'est pas bloquant pour la phase 1 puisqu'on n'a pas encore d'endpoints, mais il faudra absolument basculer vers EmailStr en phase 2 quand on exposera les endpoints.
- Deuxième point sur la performance du chiffrement. Regarde le module encryption.py. À chaque appel d'encrypt ou decrypt, on crée une nouvelle instance de Fernet à partir de la clé. C'est inutile et un peu coûteux. Idéalement on créerait l'instance Fernet une seule fois au démarrage et on la réutiliserait. Mais pour un POC avec peu de trafic, c'est acceptable. Note cela comme une optimisation potentielle pour plus tard.
- Troisième point sur la méthode get_session_by_token. Elle est implémentée dans AuthService mais elle ne sera utilisée qu'en phase 3 quand le middleware vérifiera les tokens. C'est en avance par rapport au PRD mais pas grave, juste un peu de code mort en attendant la phase 3.

## Points à ne pas négliger pour la suite du projet

### Authentification

Points traités en phase 2 et fermés.
- ~~Validation EmailStr~~ : fait en phase 2
- ~~Singleton Fernet~~ : fait en phase 2
- ~~get_session_by_token~~ : sera utilisé en phase 3

Points encore ouverts.
- D-010 dette transactionnelle dans verify_magic_link, à revoir avant 
  production ou migration PostgreSQL
- Migration de l'envoi du magic link vers Mailtrap en début de semaine 5
- Mise en place de pre-commit hooks en semaine 5
- Tests pytest avec mocks IBMPAClient en semaine 5
- Installation Alembic pour les migrations propres en semaine 5 ou 6

### Sécurité

- Stratégie de rotation de la clé Fernet à documenter
- Stratégie de backup chiffré de la base
- Cookie secure passe à True quand on déploie en HTTPS
- Investiguer HashiCorp Vault ou équivalent pour la production