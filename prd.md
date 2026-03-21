---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-02b-vision', 'step-02c-executive-summary', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish', 'step-12-complete']
inputDocuments: []
workflowType: 'prd'
classification:
  projectType: 'saas_prosumer_web'
  target: 'B2C - entrepreneurs & solopreneurs'
  domain: 'general/ecommerce-intelligence'
  complexity: 'low-medium'
  compliance: 'none'
  projectContext: 'greenfield'
  pricingInScope: false
---

# Product Requirements Document - Shipper

**Auteur :** Florian
**Date :** 2026-03-21
**Type :** SaaS Prosumer Web — Greenfield — Hackathon MVP
**Cible :** B2C — Entrepreneurs & Solopreneurs e-commerce

---

## Résumé Exécutif

Market Intelligence AI est une plateforme web SaaS qui automatise l'analyse de marché pour les entrepreneurs et solopreneurs e-commerce. L'utilisateur saisit un mot-clé ou une idée produit et observe en temps réel la construction de son tableau de bord d'analyse marché — porté par l'agrégation multi-sources et l'interprétation par LLM.

La plateforme cible des profils non-analytiques qui ont besoin de valider une idée rapidement, avant d'investir temps et capital. Elle compresse la phase de recherche marché de plusieurs jours à quelques minutes, permettant d'aligner produit et marché avant que la fenêtre d'opportunité ne se referme.

**Proposition de valeur centrale :** *Aligner votre produit au marché en un temps record.*

### Ce qui rend ce produit unique

Le différenciateur clé est la **couche de synthèse temps réel** : Market Intelligence AI ne livre pas un rapport statique — elle construit un dashboard en direct, section par section, à mesure que l'IA analyse. L'utilisateur voit l'analyse se former devant lui : produits concurrents d'abord, puis score de viabilité, persona cible, angles de différenciation.

Deuxième différenciateur : l'export Markdown structuré est conçu comme une interface de première classe pour les agents IA downstream, pas seulement un format de partage.

L'insight fondateur : les LLMs et APIs de données ont suffisamment maturé pour rendre ce pipeline accessible à un coût marginal. L'opportunité est de packager cette puissance dans un outil sans friction pour des non-analystes qui ont besoin de confiance — vite.

---

## Critères de Succès

### Succès Utilisateur

L'utilisateur saisit un keyword et observe le dashboard se construire en direct. Le moment de valeur clé est la **construction progressive en temps réel** — les premiers produits concurrents apparaissent en moins de 5 secondes, le rapport complet en moins de 60 secondes.

Succès = l'utilisateur comprend le marché de son idée sans avoir ouvert un seul onglet supplémentaire.

### Succès Produit (Hackathon)

- Pipeline complet fonctionnel bout-en-bout : saisie → pipeline IA → dashboard streaming
- Exports MD et PDF fonctionnels et partageables (humains et agents IA)
- Démonstration convaincante et compréhensible en moins de 3 minutes

### Succès Technique

- Premier événement SSE émis en moins de 5 secondes
- Streaming LLM token-par-token sans pause perceptible de plus de 3 secondes
- Pipeline résilient : continue et délivre des résultats partiels si une source est indisponible

---

## Périmètre Produit

### MVP — Hackathon (Phase 1)

**Approche :** Experience MVP — démontrer le concept sur un flux complet bout-en-bout avec données réelles.

**Sources de données :** Google Trends + Reddit + Amazon

**Capacités indispensables :**
- Saisie d'un keyword ou idée produit
- Pipeline d'analyse parallèle vers 3 sources
- Streaming SSE avec tokens LLM en temps réel, section par section
- Dashboard progressif : produits marketplace (en premier), score de viabilité, persona cible, angles de différenciation, aperçu concurrentiel
- Export Markdown sémantique (compatible agents IA)
- Export PDF

### Growth — Post-Hackathon (Phase 2)

- Sources additionnelles : X/Twitter, eBay
- Historique des analyses et comparaison d'idées
- API consommable par agents externes
- Deep-dive concurrentiel

### Vision (Phase 3)

- Monitoring marché en temps réel avec alertes
- Collaboration en équipe
- Rapports en marque blanche

### Gestion des Risques

| Risque | Mitigation |
|---|---|
| Rate-limiting / blocage sources | Plan de secours : données simulées activables en urgence uniquement |
| Latence LLM | Streaming token-par-token — l'effet visuel reste convaincant même si la génération prend du temps |
| Dérapage de scope | Sources réduites à 3 pour le MVP — X et eBay post-MVP |

---

## Parcours Utilisateurs

### Parcours 1 — L'Entrepreneur (chemin nominal)

*Maya, solopreneuse, a une idée de produit beauté eco-friendly. Elle a trop souvent lancé des idées sans valider le marché. Cette fois, elle veut des données avant d'investir.*

1. Elle saisit "eco-friendly bamboo skincare" dans le champ de recherche
2. Les premiers produits Amazon apparaissent en direct — elle voit immédiatement les concurrents, leurs prix, leurs liens
3. Le score de viabilité se construit (74/100), suivi du persona cible : "Femme 25-35, urbaine, sensible à l'impact environnemental..."
4. Les angles de différenciation émergent : packaging zéro déchet, certification B-Corp, prix accessible
5. En 5 minutes, Maya a une image claire. Elle exporte le rapport en PDF et le partage avec son associée.

*Avant : 2 jours de recherche Google, Reddit, Amazon. Après : 5 minutes, décision prise.*

### Parcours 2 — L'Agent IA (consommateur MD)

*Un agent de veille concurrentielle automatisé tourne chaque semaine pour un entrepreneur.*

1. L'agent soumet un keyword à la plateforme
2. Reçoit l'export Markdown structuré (headings prévisibles, scores parsables)
3. L'intègre dans son contexte pour générer des recommandations hebdomadaires

*Ce parcours révèle : structure MD sémantique et schéma stable sont des exigences, pas des options.*

### Parcours 3 — L'Entrepreneur (résultats décevants)

Maya teste une idée qui score 28/100. Le dashboard lui montre pourquoi : marché saturé, faible différenciation possible. Elle pivote vers une autre idée en 10 minutes.

*Ce parcours révèle : la valeur est aussi dans le "non". Un score bas doit être aussi lisible et actionnable qu'un score haut.*

---

## Innovation & Différenciation

### Streaming UX — Dashboard à Construction Progressive

L'expérience centrale rompt avec le modèle submit/wait/receive de tous les outils de market research existants (Jungle Scout, Helium 10, Semrush). Le dashboard se construit en direct, créant un sentiment d'immédiateté et de transparence impossible à reproduire avec un rapport statique.

Les produits marketplace sont scrapés en priorité dans le pipeline — premier résultat visible en moins de 5 secondes — maximisant l'impact perçu dès les premières secondes.

### Export MD comme Interface Agent IA

L'export Markdown n'est pas un format secondaire — c'est une interface conçue pour être consommée par des agents IA downstream. La plateforme se positionne comme un nœud dans un workflow agentique. Le schéma MD (headings prévisibles, scores en format parsable) constitue un contrat stable pour les consommateurs automatisés.

### Risques d'Innovation

| Risque | Mitigation |
|---|---|
| Streaming : latence perçue trop élevée | Fallback vers affichage par blocs complétés |
| MD structuré : schéma instable casse les agents | Définir et geler le schéma dès le MVP |

---

## Architecture Technique

### Stack

- **Framework :** SvelteKit (rendu hybride SSR/SPA selon les routes)
- **Streaming :** Server-Sent Events (SSE) — communication serveur → client unidirectionnelle
- **Authentification :** aucune — usage stateless, sans session persistante

### Pipeline d'Analyse

1. Réception du keyword utilisateur
2. Scraping marketplace (Amazon) en priorité → premier événement SSE émis
3. Requêtes parallèles vers les autres sources (Google Trends, Reddit)
4. Agrégation et normalisation des données
5. Interprétation et scoring par LLM, streamé token-par-token
6. Génération des exports MD et PDF à la fin du pipeline

### Sources de Données MVP

| Catégorie | Source | Priorité pipeline |
|---|---|---|
| Marketplace | Amazon | 1 — émis en premier |
| Analytics | Google Trends | 2 |
| Social | Reddit | 2 |
| Synthèse | LLM | 3 — après agrégation |

### Schéma des Événements SSE

Les noms d'événements sont stables dès le MVP (contrat pour consommateurs agents) :
`marketplace_products` → `viability_score` → `target_persona` → `differentiation_angles` → `competitive_overview` → `export_ready`

### Contraintes d'Implémentation

- Timeout par source : 10 secondes — le pipeline continue sans elle
- Schéma MD export figé dès le MVP (headings prévisibles, scores parsables)
- Desktop web prioritaire — mobile-first hors scope hackathon

---

## Exigences Fonctionnelles

### Saisie & Lancement

- FR1 : L'utilisateur peut saisir un keyword ou une description d'idée produit en langage naturel
- FR2 : L'utilisateur peut lancer l'analyse depuis la saisie sans étape de configuration supplémentaire
- FR3 : Le système valide que la saisie contient un contenu exploitable avant de démarrer le pipeline
- FR4 : L'utilisateur peut voir l'état d'avancement de l'analyse en cours
- FR5 : Le dashboard affiche un état squelette entre le lancement et la réception du premier événement SSE

### Collecte de Données

- FR6 : Le système scrape Amazon en priorité pour récupérer les produits existants (titre, prix, lien) et les émet en premier via SSE
- FR7 : Le système interroge Google Trends pour les signaux de demande associés au keyword
- FR8 : Le système interroge Reddit pour les signaux de sentiment et de validation communautaire
- FR9 : Le système continue le pipeline si une source dépasse 10 secondes de timeout
- FR10 : Le système informe l'utilisateur lorsqu'une source est indisponible et que les résultats sont partiels
- FR11 : Le système agrège et normalise les données issues des sources multiples

### Analyse & Scoring

- FR12 : Le système génère un score de viabilité marché basé sur les données agrégées
- FR13 : Le système génère un persona cible représentatif du segment de marché identifié
- FR14 : Le système génère des angles de différenciation actionnables pour l'idée soumise
- FR15 : Le système génère un aperçu du paysage concurrentiel pertinent
- FR16 : Le système interprète et synthétise les données brutes via LLM pour produire des insights actionnables
- FR17 : Le score de viabilité est aussi lisible et actionnable pour un résultat bas que pour un résultat haut

### Streaming Dashboard

- FR18 : Les sections du dashboard apparaissent progressivement au fil de leur génération, sans attendre la fin du pipeline
- FR19 : Le contenu LLM est streamé token-par-token, section par section
- FR20 : Chaque section apparaît dès qu'elle est disponible, indépendamment des autres
- FR21 : L'utilisateur peut distinguer les sections en cours de génération des sections complètes

### Contenu du Dashboard

- FR22 : Le dashboard affiche les produits existants sur le marché avec titre, prix indicatif et lien direct vers leur page marketplace
- FR23 : L'utilisateur peut accéder directement à un produit concurrent depuis le dashboard via son lien
- FR24 : Le dashboard affiche le score de viabilité avec une explication de ce qui le détermine
- FR25 : Le dashboard affiche le persona cible avec ses caractéristiques clés
- FR26 : Le dashboard affiche les angles de différenciation sous forme actionnable
- FR27 : Le dashboard affiche l'aperçu concurrentiel avec les acteurs identifiés

### Export & Partage

- FR28 : L'utilisateur peut exporter le rapport complet en Markdown structuré
- FR29 : L'export Markdown suit un schéma sémantique stable (headings prévisibles, scores en format parsable)
- FR30 : L'utilisateur peut exporter le rapport complet en PDF
- FR31 : L'export est disponible à la fin de la génération du rapport complet

### Post-MVP

- FR32 : *(Post-MVP)* Le système suggère des reformulations du keyword si la saisie est trop générique ou ambiguë

---

## Exigences Non-Fonctionnelles

### Performance

- NFR1 : Le premier événement SSE (produits marketplace) est émis en moins de 5 secondes après le lancement de l'analyse
- NFR2 : Le rapport complet est généré en moins de 60 secondes dans des conditions normales de disponibilité des sources
- NFR3 : Le streaming LLM est continu — aucune pause de plus de 3 secondes entre les tokens d'une même section
- NFR4 : Le pipeline délivre des résultats partiels même si une source dépasse 10 secondes de timeout

### Sécurité

- NFR5 : Toutes les communications client-serveur sont chiffrées via HTTPS/TLS
- NFR6 : Aucune donnée utilisateur (keyword, résultats) n'est persistée côté serveur au-delà de la durée de la session
