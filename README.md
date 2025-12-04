# UltimateScraper

---

````
ultimate-crawler/
├─ README.md
├─ pyproject.toml
├─ requirements.txt
├─ .gitignore
│
├─ configs/
│  ├─ job_wine.yaml
│  └─ job_XXX.yaml
│
├─ data/
│  ├─ jobs/
│  │  └─ ... (par job)
│  └─ cache/
│     ├─ robots/
│     └─ embeddings/
│
├─ scripts/
│  ├─ run_job.py              # lance un job de crawl complet
│  └─ debug_single_url.py     # teste la pipeline sur 1 URL
│
└─ src/
   └─ ultimate_crawler/
      ├─ __init__.py
      │
      ├─ config/
      │  ├─ __init__.py
      │  └─ loader.py         # charge YAML, dataclasses JobConfig
      │
      ├─ discovery/
      │  ├─ __init__.py
      │  ├─ search_api.py     # interface vers moteur (ex: SerpAPI / autre)
      │  └─ domain_selector.py# clean + déduplique domaines
      │
      ├─ crawl/
      │  ├─ __init__.py
      │  ├─ frontier.py       # queue d’URLs, priorités, déjà vus
      │  ├─ scheduler.py      # logique d’ordre de crawl (BFS/DFS, domains)
      │  ├─ fetcher.py        # requests + (option) Playwright
      │  ├─ robots.py         # gestion robots.txt
      │  ├─ html_storage.py   # optionnel: snapshot HTML
      │  └─ parser.py         # trafilatura -> text brut
      │
      ├─ relevance/
      │  ├─ __init__.py
      │  ├─ language.py       # détection langue
      │  ├─ keyword_filter.py # simple score par mots-clés
      │  ├─ embedding_model.py# init sentence-transformer
      │  ├─ embedding_filter.py# score via cosinus
      │  └─ clfdoc_model.py   # (optionnel) modèle maison multi-task plus tard
      │
      ├─ core/
      │  ├─ __init__.py
      │  ├─ job_runner.py     # orchestre un job complet
      │  ├─ metrics.py        # stats: nb pages, domains, taille, etc.
      │  └─ utils.py
      │
      └─ io/
         ├─ __init__.py
         ├─ writers.py        # JSONLWriter, ParquetWriter, rotation de fichier (taille)
         └─ logging_setup.py
````