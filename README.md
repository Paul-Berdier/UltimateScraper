# 🕸️ UltimateScraper — The Ultimate Multilingual, Keyword-Driven Web Crawler

### *Massive automated data collection for domain-specific AI training (Wine, Cosmetics, Fraud, etc.)*

UltimateScraper est un **crawler / scraper intelligent**, modulaire et paramétrable, conçu pour :

* découvrir automatiquement de nouveaux sites à partir de **mots-clés** ;
* explorer le Web dans plusieurs **langues** ;
* filtrer les pages par **pertinence sémantique** (embeddings multilingues) ;
* respecter des limites strictes (**mémoire**, **pages**, **domaines**) ;
* produire un **corpus propre**, prêt pour l’entraînement de modèles IA.

Il ne dépend d’aucun moteur externe : l’utilisateur fournit simplement des **keywords**, des **langues**, et des **contraintes**, et le système récupère *tout ce qui est pertinent* sur le Web.

Ce projet sert de fondation à la construction de jeux de données massifs pour des modèles **encodeur-décodeur spécialisés** (ex. : vins, cosmétique, agriculture, produits sécurisés).

---

# ✨ Fonctionnalités majeures

### 🔍 Recherche intelligente de nouvelles sources

* Entrée : mots-clés + langues
* Découverte automatique de domaines à explorer
* Déduplication et normalisation des sites

### 🕷️ Crawler robuste

* Requests + Politeness Policier (delay configurable)
* Gestion robots.txt
* File d’attente d’URLs (Frontier BFS)
* Scheduler par domaine (limite pages/domaines)
* Mode 100% Python (pas besoin de Selenium)

### 🧠 Filtrage IA de la pertinence

* Embeddings multilingues (`sentence-transformers`)
* Similarité cosinus entre mots-clés ↔ contenu
* Détection de langue automatique
* Mode fallback "keyword relevance" disponible

### 🧹 Extraction de texte propre

* `trafilatura` pour nettoyer HTML → texte
* Suppression du bruit, métadonnées, structure Web

### 💾 Stockage optimisé

* Sorties en JSONL (raw + filtered)
* Writer rotatif en cas de gros volumes
* Counting mémoire pour arrêter le job automatiquement

---

# 📂 Structure du projet

```
ultimate-crawler/
├─ README.md
├─ pyproject.toml
├─ requirements.txt
├─ .gitignore
│
├─ configs/
│  ├─ job_wine.yaml        # Exemple de job
│  └─ job_XXX.yaml         # Autres jobs
│
├─ data/
│  ├─ jobs/                # Outputs par job
│  └─ cache/
│     ├─ robots/           # Cache robots.txt
│     └─ embeddings/       # (optionnel) cache d'embeddings
│
├─ scripts/
│  ├─ run_job.py           # Lance un job complet
│  └─ debug_single_url.py  # Tester toute la pipeline sur 1 URL
│
└─ src/
   └─ ultimate_crawler/
      ├─ config/           # Chargement YAML + dataclasses
      ├─ discovery/        # Recherche de domaines
      ├─ crawl/            # Frontier, fetcher, scheduler, parser
      ├─ relevance/        # Embeddings, langue, filtres
      ├─ core/             # JobRunner + métriques
      └─ io/               # Writers JSONL + logging
```

---

# 🚀 Installation

## 1. Créer un environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.\.venv\Scripts\activate    # Windows PowerShell
```

## 2. Installer UltimateScraper

À la racine du projet :

```bash
pip install -e .
```

## 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

# ⚙️ Configuration d’un job

Les jobs sont définis dans `configs/job_*.yaml`.

Exemple (`configs/job_wine.yaml`) :

```yaml
job_name: "wine_multilingual_crawl"

keywords:
  - "vin"
  - "wine"
  - "vino"
  - "葡萄酒"

languages: ["fr", "en", "es", "zh"]

limits:
  max_domains: 200
  max_pages: 20000
  memory_limit_mb: 10240
  max_pages_per_domain: 500

crawler:
  user_agent: "UltimateCrawler/1.0"
  request_timeout: 10
  obey_robots_txt: true
  politeness_delay: 0.5

relevance:
  min_chars: 400
  relevance_threshold: 0.35
  model: "embedding"
  embedding_model_name: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

output:
  dir: "data/jobs/wine_multilingual"
  raw_pages_file: "raw_pages.jsonl"
  filtered_docs_file: "docs_filtered.jsonl"

seeds:
  - "https://www.winefolly.com/"
  - "https://www.hachette-vins.com/"
```

---

# ▶️ Lancement d’un job

Depuis la racine :

```bash
python scripts/run_job.py -c configs/job_wine.yaml
```

Sortie attendue :

```
=== Job: wine_multilingual_crawl ===
[INFO] Seeds found: 4
[INFO] Job finished.
```

Les fichiers générés :

```
data/jobs/wine_multilingual/
│
├─ raw_pages.jsonl
└─ docs_filtered.jsonl
```

---

# 🔍 Debug sur une URL unique

```bash
python scripts/debug_single_url.py -c configs/job_wine.yaml -u "https://www.winefolly.com/"
```

Affiche :

* détected language
* extracted text length
* relevance score
* éventuels warnings

---

# 📄 Format de sortie

Chaque document est stocké en JSONL :

```json
{
  "url": "https://exemple.com/vin-du-rhone",
  "domain": "exemple.com",
  "lang": "fr",
  "text": "Les vins du Rhône se caractérisent par...",
  "score_relevance": 0.81
}
```

Ces fichiers JSONL peuvent ensuite servir pour :

* entraînement d’un **modèle encodeur-décodeur spécialisé "vin"**,
* construction d’un corpus multilingue,
* segmentation / labeling automatiques,
* génération de datasets QA / résumé / classification.

---

# 🔧 Points d’extension (IA Ready)

UltimateScraper est conçu pour accueillir des modules IA custom :

### Plug-in model ClfDoc maison

→ Filtrage par classification automatique de page (vin / pas vin / type)

### Plug-in NER / Slot Extraction

→ Extraction automatique de :

* cépages
* régions
* appellations
* note de dégustation
* domaine / producteur

### Plug-in MT5 ou Qwen

→ Résumé automatique
→ Normalisation du contenu
→ Génération de descriptions marketing

---

# 📈 Roadmap

### Phase 1 — Terminé

✔️ Crawler minimal complet
✔️ Filtrage embeddings multilingue
✔️ Extraction texte propre (trafilatura)
✔️ Gestion seeds + limites + robots.txt
✔️ Architecture modulaire clean

### Phase 2 — À venir

🟦 Intégration de ton modèle ClfDoc
🟦 Extraction NER vin (SlotNER maison)
🟦 Préparation automatique de dataset pour modèle encodeur-décodeur
🟦 Support Playwright pour JS heavy sites
🟦 Multi-crawler distributed (Ray / multiprocessing)

---

# 👨‍💻 Auteur & Objectif

Projet initié par **Paul Berdier**, Data Scientist chez Prooftag.
Fait pour construire un **crawler IA professionnel**, scalable, modulaire, et capable de générer automatiquement des datasets propres pour entraîner des modèles spécialisés (vin, cosmétique, sécurité produit, etc.).
