#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set

from ultimate_crawler.ner import WineSlotExtractor

# =============================================================================
# Configuration globale
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent

LOGGER = logging.getLogger("wine_slot_annotator")


# =============================================================================
# Utils
# =============================================================================

def load_csv_column(
    csv_path: Path,
    column: str,
    *,
    lower: bool = True,
    drop_na: bool = True,
) -> List[str]:
    """
    Charge une colonne d'un CSV et renvoie une liste unique triée.

    Paramètres
    ----------
    csv_path : Path
        Chemin du fichier CSV.
    column : str
        Nom de la colonne à extraire.
    lower : bool, optionnel
        Si True, renvoie toutes les valeurs en minuscules.
    drop_na : bool, optionnel
        Si True, supprime les valeurs 'NA' / ' NA' (case-insensitive).

    Retour
    ------
    List[str]
        Liste triée des valeurs uniques.
    """
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV introuvable : {csv_path}")

    values: Set[str] = set()
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if column not in (reader.fieldnames or []):
            raise ValueError(
                f"Colonne '{column}' introuvable dans {csv_path} "
                f"(colonnes disponibles : {reader.fieldnames})"
            )

        for row in reader:
            raw = row.get(column) or ""
            val = raw.strip()
            if not val:
                continue

            # Gestion des NA
            if drop_na and val.upper().replace(" ", "") == "NA":
                continue

            values.add(val.lower() if lower else val)

    sorted_values = sorted(values)
    LOGGER.info(
        "Chargé %d valeurs uniques depuis %s (colonne='%s')",
        len(sorted_values),
        csv_path,
        column,
    )
    return sorted_values


# =============================================================================
# Config annotateur
# =============================================================================

@dataclass
class LexiconConfig:
    grapes: List[str]
    regions: List[str]
    appellations: List[str]


def load_lexicons(lwin_dir: Path) -> LexiconConfig:
    """
    Charge les lexiques nécessaires à partir des CSV LWIN.

    Paramètres
    ----------
    lwin_dir : Path
        Dossier contenant les CSV (grape_variety.csv, sub_region.csv, region.csv, ...).

    Retour
    ------
    LexiconConfig
        Cépages, régions, appellations prêts pour le WineSlotExtractor.
    """
    LOGGER.info("Chargement des lexiques LWIN depuis : %s", lwin_dir)

    grapes_csv = lwin_dir / "grape_variety.csv"
    sub_region_csv = lwin_dir / "sub_region.csv"
    region_csv = lwin_dir / "region.csv"

    grapes = load_csv_column(
        grapes_csv,
        column="grape_variety_name",
        lower=True,
        drop_na=True,
    )

    appellations = load_csv_column(
        sub_region_csv,
        column="sub_region_name",
        lower=True,
        drop_na=True,
    )

    regions = load_csv_column(
        region_csv,
        column="region_name",
        lower=True,
        drop_na=True,
    )

    return LexiconConfig(
        grapes=grapes,
        regions=regions,
        appellations=appellations,
    )


# =============================================================================
# Core
# =============================================================================

def annotate_file(
    input_path: Path,
    output_path: Path,
    extractor: WineSlotExtractor,
    max_docs: int | None = None,
) -> int:
    """
    Annote un fichier JSONL avec les slots de vin.

    Paramètres
    ----------
    input_path : Path
        Fichier JSONL d'entrée (un objet JSON par ligne, avec au moins 'text').
    output_path : Path
        Fichier JSONL de sortie.
    extractor : WineSlotExtractor
        Extracteur de slots.
    max_docs : int | None
        Si non None, limite le nombre de documents traités (utile pour des tests rapides).

    Retour
    ------
    int
        Nombre de documents effectivement annotés.
    """
    if not input_path.is_file():
        raise FileNotFoundError(f"Fichier d'entrée introuvable : {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    LOGGER.info("Annotation des documents : %s -> %s", input_path, output_path)
    if max_docs is not None:
        LOGGER.info("Limite de documents : %d", max_docs)

    count = 0
    with input_path.open(encoding="utf-8") as fin, output_path.open(
        "w", encoding="utf-8"
    ) as fout:
        for line in fin:
            if not line.strip():
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                LOGGER.warning("Ligne JSON invalide (ignorée) : %s", e)
                continue

            text = obj.get("text", "")
            if not isinstance(text, str):
                LOGGER.debug("Champ 'text' manquant ou non textuel, id=%r", obj.get("id"))
                text = str(text)

            slots = extractor.extract(text).to_dict()
            obj["wine_slots"] = slots

            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
            count += 1

            if max_docs is not None and count >= max_docs:
                break

    LOGGER.info("Annotation terminée : %d documents -> %s", count, output_path)
    return count


# =============================================================================
# CLI
# =============================================================================

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Annotate JSONL docs with wine slots using LWIN lexicons."
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Fichier JSONL d'entrée (ex: docs_filtered.jsonl)",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Fichier JSONL de sortie avec les slots (ex: docs_with_slots.jsonl)",
    )
    parser.add_argument(
        "--lwin-dir",
        type=str,
        default=str(BASE_DIR / "data" / "lwin"),
        help="Dossier contenant les CSV LWIN (défaut: ./data/lwin)",
    )
    parser.add_argument(
        "--max-docs",
        type=int,
        default=None,
        help="Nombre maximal de documents à annoter (pour tests).",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Niveau de log (défaut: INFO).",
    )
    return parser


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    setup_logging(args.log_level)

    input_path = Path(args.input)
    output_path = Path(args.output)
    lwin_dir = Path(args.lwin_dir)

    LOGGER.info("=== Wine Slot Annotator ===")
    LOGGER.info("Input : %s", input_path)
    LOGGER.info("Output: %s", output_path)
    LOGGER.info("LWIN dir: %s", lwin_dir)

    # Chargement des lexiques
    lexicons = load_lexicons(lwin_dir)

    # Initialisation de l'extracteur
    extractor = WineSlotExtractor(
        grape_lexicon=lexicons.grapes,
        region_lexicon=lexicons.regions,
        appellation_lexicon=lexicons.appellations,
    )

    # Annotation
    total = annotate_file(
        input_path=input_path,
        output_path=output_path,
        extractor=extractor,
        max_docs=args.max_docs,
    )

    print(f"[INFO] Annotated {total} docs with wine slots -> {output_path}")


if __name__ == "__main__":
    main()
