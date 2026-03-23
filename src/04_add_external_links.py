"""
Step 4: Add external links to Wikidata and DBpedia.

Usage:
    python 04_add_external_links.py

Reads the JSON files, queries Wikidata for authors/institutions/concepts,
and produces external_links.ttl with owl:sameAs, skos:closeMatch, etc.

NOTE: This script requires internet access to query Wikidata's API.
If offline, it will generate a template file you can fill in manually.
"""
import csv
import json
import time
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    raise

try:
    from rdflib import Graph, Namespace, Literal, URIRef
    from rdflib.namespace import RDF, RDFS, OWL, SKOS, FOAF
except ImportError:
    print("Install rdflib: pip install rdflib")
    raise

from config import JSON_DIR, OUTPUT_DIR, INST_NS, HINT_NS

INST = Namespace(INST_NS)
HINT = Namespace(HINT_NS)
WD = Namespace("http://www.wikidata.org/entity/")
DBR = Namespace("http://dbpedia.org/resource/")
AUDIT_DIR = OUTPUT_DIR / "audit"


def search_wikidata(query: str, entity_type: str = None) -> dict | None:
    """
    Search Wikidata for an entity by label.
    Returns {qid, label, description} or None.
    """
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "format": "json",
        "limit": 3,
    }
    if entity_type:
        params["type"] = entity_type

    try:
        resp = requests.get(url, params=params, timeout=10,
                           headers={"User-Agent": "HI-Ontology-Pipeline/1.0 (university project)"})
        resp.raise_for_status()
        results = resp.json().get("search", [])
        if results:
            top = results[0]
            return {
                "qid": top["id"],
                "label": top.get("label", ""),
                "description": top.get("description", ""),
                "uri": f"http://www.wikidata.org/entity/{top['id']}"
            }
    except Exception as e:
        print(f"    Wikidata query failed for '{query}': {e}")

    return None


def record_link_action(actions: list[dict], category: str, subject: str,
                       predicate: str = "", target: str = "",
                       status: str = "linked", note: str = ""):
    """Append one structured linking action for later auditing."""
    actions.append({
        "category": category,
        "subject": subject,
        "predicate": predicate,
        "target": target,
        "status": status,
        "note": note,
    })


def write_external_link_audit(actions: list[dict], total_link_triples: int):
    """Write external linking actions and summary counts."""
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = AUDIT_DIR / "external_linking_actions.csv"
    summary_path = AUDIT_DIR / "external_linking_summary.json"

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["category", "subject", "predicate", "target", "status", "note"],
        )
        writer.writeheader()
        writer.writerows(actions)

    linked_counts_by_category = {}
    unresolved_counts_by_category = {}
    predicate_counts = {}
    for action in actions:
        category = action["category"]
        predicate = action["predicate"]
        if action["status"] == "linked":
            linked_counts_by_category[category] = linked_counts_by_category.get(category, 0) + 1
            if predicate:
                predicate_counts[predicate] = predicate_counts.get(predicate, 0) + 1
        else:
            unresolved_counts_by_category[category] = unresolved_counts_by_category.get(category, 0) + 1

    summary = {
        "total_actions": len(actions),
        "linked_actions": sum(1 for a in actions if a["status"] == "linked"),
        "unresolved_actions": sum(1 for a in actions if a["status"] != "linked"),
        "total_link_triples_written": total_link_triples,
        "linked_counts_by_category": linked_counts_by_category,
        "unresolved_counts_by_category": unresolved_counts_by_category,
        "predicate_counts": predicate_counts,
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


# ── Predefined concept mappings ───────────────────────────────
# Comprehensive, manually verified mappings from HINT concepts
# to Wikidata/DBpedia. Each concept can have multiple links.
from expanded_concept_mappings import CONCEPT_MAPPINGS, INSTANCE_LINKS


def main():
    g = Graph()
    g.bind("inst", INST)
    g.bind("hint", HINT)
    g.bind("owl", OWL)
    g.bind("skos", SKOS)
    g.bind("foaf", FOAF)
    g.bind("rdfs", RDFS)
    g.bind("wd", WD)
    g.bind("dbr", DBR)

    link_count = 0
    audit_actions = []

    # ── 1. Static concept mappings (always works, no API needed) ──
    print("=== Adding static concept mappings ===")
    for hint_concept, link_list in CONCEPT_MAPPINGS.items():
        local = hint_concept.replace("hint:", "")
        subject = HINT[local]

        for predicate_str, target_uri in link_list:
            target = URIRef(target_uri)

            if predicate_str == "skos:closeMatch":
                g.add((subject, SKOS.closeMatch, target))
            elif predicate_str == "skos:relatedMatch":
                g.add((subject, SKOS.relatedMatch, target))
            elif predicate_str == "rdfs:seeAlso":
                g.add((subject, RDFS.seeAlso, target))
            elif predicate_str == "owl:sameAs":
                g.add((subject, OWL.sameAs, target))

            link_count += 1
            record_link_action(
                audit_actions,
                "static_concept_mapping",
                str(subject),
                predicate_str,
                target_uri,
                "linked",
            )

    print(f"  Added {link_count} static concept links")

    # ── 2. Manual instance links (conference etc.) ────────────
    print("\n=== Adding instance links ===")
    for inst_ref, link_list in INSTANCE_LINKS.items():
        local = inst_ref.replace("inst:", "")
        subject = INST[local]

        for predicate_str, target_uri in link_list:
            target = URIRef(target_uri)

            if predicate_str == "owl:sameAs":
                g.add((subject, OWL.sameAs, target))
            elif predicate_str == "rdfs:seeAlso":
                g.add((subject, RDFS.seeAlso, target))

            link_count += 1
            print(f"  {inst_ref} -> {target_uri}")
            record_link_action(
                audit_actions,
                "manual_instance_link",
                str(subject),
                predicate_str,
                target_uri,
                "linked",
            )

    # ── 3. Conference link (hardcoded as backup) ──────────────
    conf_uri = INST["HHAI2025"]
    # Add if not already added via INSTANCE_LINKS
    if (conf_uri, OWL.sameAs, None) not in g:
        g.add((conf_uri, OWL.sameAs, URIRef("http://www.wikidata.org/entity/Q113466830")))
        link_count += 1
        print("  HHAI 2025 -> Q113466830 (hardcoded)")
        record_link_action(
            audit_actions,
            "hardcoded_conference_link",
            str(conf_uri),
            "owl:sameAs",
            "http://www.wikidata.org/entity/Q113466830",
            "linked",
        )

    # ── 4. Author and institution links (from JSON files) ─────
    print("\n=== Linking authors and institutions ===")
    json_files = sorted(JSON_DIR.glob("*.json"))

    seen_authors = set()
    seen_affiliations = set()

    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if "_error" in data:
            continue

        source_id = json_file.stem
        prefix = source_id.replace("_", "").capitalize()
        # Match the URI pattern from 03_generate_instances.py
        # sanitize_uri converts "paper_01" -> "Paper01" etc.
        import re
        parts = source_id.strip().split('_')
        prefix = parts[0].capitalize() + ''.join(w.capitalize() for w in parts[1:])

        for i, author in enumerate(data.get("authors", []), 1):
            name = author.get("name", "")
            if not name or name in seen_authors:
                continue
            seen_authors.add(name)

            author_uri_local = f"{prefix}_Author{i}"
            author_uri = INST[author_uri_local]

            # Search Wikidata for author
            result = search_wikidata(name, "item")
            if result and "researcher" in result.get("description", "").lower() or \
               result and "scientist" in result.get("description", "").lower() or \
               result and "professor" in result.get("description", "").lower() or \
               result and "computer" in result.get("description", "").lower():
                g.add((author_uri, OWL.sameAs, URIRef(result["uri"])))
                print(f"  {name} -> {result['uri']} ({result['description']})")
                link_count += 1
                record_link_action(
                    audit_actions,
                    "author_wikidata",
                    str(author_uri),
                    "owl:sameAs",
                    result["uri"],
                    "linked",
                    result.get("description", ""),
                )
            else:
                print(f"  {name} -> not found / no confident match")
                record_link_action(
                    audit_actions,
                    "author_wikidata",
                    str(author_uri),
                    "owl:sameAs",
                    "",
                    "unresolved",
                    "not found / no confident match",
                )

            # Institution
            aff = author.get("affiliation", "")
            if aff and aff not in seen_affiliations:
                seen_affiliations.add(aff)
                aff_id = re.sub(r'[^\w\s-]', '', aff).strip().split()
                aff_id = aff_id[0].capitalize() + ''.join(w.capitalize() for w in aff_id[1:]) if aff_id else "Unknown"
                aff_uri = INST[f"Affiliation_{aff_id}"]

                result = search_wikidata(aff, "item")
                if result and ("university" in result.get("description", "").lower() or
                               "institute" in result.get("description", "").lower() or
                               "research" in result.get("description", "").lower() or
                               "organization" in result.get("description", "").lower()):
                    g.add((aff_uri, OWL.sameAs, URIRef(result["uri"])))
                    print(f"  {aff} -> {result['uri']} ({result['description']})")
                    link_count += 1
                    record_link_action(
                        audit_actions,
                        "affiliation_wikidata",
                        str(aff_uri),
                        "owl:sameAs",
                        result["uri"],
                        "linked",
                        result.get("description", ""),
                    )
                else:
                    print(f"  {aff} -> not found / no confident match")
                    record_link_action(
                        audit_actions,
                        "affiliation_wikidata",
                        str(aff_uri),
                        "owl:sameAs",
                        "",
                        "unresolved",
                        "not found / no confident match",
                    )

            time.sleep(0.5)  # rate limiting

    # ── Save ──────────────────────────────────────────────────
    output_path = OUTPUT_DIR / "external_links.ttl"
    g.serialize(destination=str(output_path), format="turtle")
    write_external_link_audit(audit_actions, link_count)

    print(f"\n=== Done ===")
    print(f"Total external links: {link_count}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
