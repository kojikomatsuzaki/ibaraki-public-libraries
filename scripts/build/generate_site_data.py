import os
import sys
import csv
import glob
import json
import re

# Import canonical YAML parser from our validator
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "validate"))
from canonical_data_validator import parse_simple_yaml

def parse_full_source_yaml(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    def extract(pattern):
        m = re.search(pattern, text)
        return m.group(1) if m else None

    sid = extract(r'source_id:\s*"([^"]+)"')
    title_ja = extract(r'title:\s*\n\s*ja:\s*"([^"]+)"')
    creator = extract(r'creator:\s*\n\s*name:\s*"([^"]+)"')
    pub_date = extract(r'publication_date:\s*"([^"]+)"')
    last_mod = extract(r'last_modified:\s*"([^"]+)"')
    url = extract(r'url:\s*"([^"]+)"')
    acc_date = extract(r'accessed_date:\s*"([^"]+)"')
    stype = extract(r'source_type:\s*"([^"]+)"')
    v_status = extract(r'verification:\s*\n\s*status:\s*"([^"]+)"')
    v_at = extract(r'verified_at:\s*"([^"]+)"')
    v_scope = extract(r'scope:\s*"([^"]+)"')

    num = int(sid.split("-")[1]) if sid and "-" in sid else 0
    return {
        "source_id": sid,
        "ref_number": num,
        "title_ja": title_ja,
        "creator": creator,
        "publication_date": pub_date,
        "last_modified": last_mod,
        "url": url,
        "accessed_date": acc_date,
        "source_type": stype,
        "verification": {
            "status": v_status,
            "verified_at": v_at,
            "scope": v_scope
        }
    }


def generate_exports(repo_root=None):
    if repo_root is None:
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    out_dir = os.path.join(repo_root, "docs", "data")
    os.makedirs(out_dir, exist_ok=True)

    master_path = os.path.join(repo_root, "data", "municipalities", "master_municipalities.json")
    registry_path = os.path.join(repo_root, "data", "municipalities", "audit_registry.json")

    with open(master_path, "r", encoding="utf-8") as f:
        master = json.load(f)
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    # 1. Sources
    source_files = sorted(glob.glob(os.path.join(repo_root, "data", "sources", "SRC-*.yaml")))
    sources_list = [parse_full_source_yaml(sf) for sf in source_files]
    sources_map = {s["source_id"]: s for s in sources_list}

    with open(os.path.join(out_dir, "sources.json"), "w", encoding="utf-8") as f:
        json.dump({"sources": sources_list}, f, ensure_ascii=False, indent=2)

    # 2. Municipalities & Facilities
    yaml_files = sorted(glob.glob(os.path.join(repo_root, "data", "libraries", "*.yaml")))
    municipalities_out = []
    flat_facilities = []

    facility_level_collection_sum = 0
    system_aggregate_collection_sum = 0

    for yf in yaml_files:
        doc = parse_simple_yaml(yf)
        code = doc["municipality_code"]
        reg_entry = registry.get(code, {})
        doc["pillars"] = reg_entry.get("pillars", {})

        for fac in doc["facilities"]:
            # Add ref numbers for cross-referencing
            fac["ref_numbers"] = sorted([
                sources_map[sid]["ref_number"]
                for sid in fac.get("sources", [])
                if sid in sources_map
            ])
            stats = fac.get("statistics", {})
            col = stats.get("collection_count")
            scope = stats.get("scope")
            if isinstance(col, int):
                if scope == "facility_level":
                    facility_level_collection_sum += col
                elif scope == "system_aggregate":
                    system_aggregate_collection_sum += col

            flat_facilities.append({
                "facility_id": fac.get("facility_id"),
                "municipality_code": code,
                "municipality_name": doc.get("municipality_name"),
                "municipality_name_en": doc.get("municipality_name_en"),
                "municipality_audit_status": doc.get("audit_status"),
                "name": fac.get("name"),
                "name_en": fac.get("name_en"),
                "category": fac.get("category"),
                "legal_status": fac.get("legal_status"),
                "postal_code": fac.get("postal_code"),
                "address": fac.get("address"),
                "phone": fac.get("phone"),
                "fax": fac.get("fax"),
                "established_year_month": fac.get("established_year_month"),
                "opened_year_month": fac.get("opened_year_month"),
                "building_structure": fac.get("building_structure"),
                "floor_area_m2": fac.get("floor_area_m2"),
                "reading_seats": fac.get("reading_seats"),
                "statistics_scope": scope,
                "fiscal_year": stats.get("fiscal_year"),
                "basis_date": stats.get("basis_date"),
                "collection_count": col,
                "annual_loans": stats.get("annual_loans"),
                "breakdown": stats.get("breakdown"),
                "sources": fac.get("sources", []),
                "ref_numbers": fac.get("ref_numbers", []),
                "field_sources": fac.get("field_sources", {}),
                "verification_status": fac.get("verification", {}).get("status"),
                "verified_at": fac.get("verification", {}).get("verified_at"),
                "verification_scope": fac.get("verification", {}).get("scope"),
                "unverified_fields": fac.get("verification", {}).get("unverified_fields", [])
            })

        municipalities_out.append(doc)

    dataset_payload = {
        "metadata": {
            "title_ja": "茨城県公立図書館データベース (Canonical Dataset)",
            "title_en": "Ibaraki Public Libraries Open Database (Canonical Dataset)",
            "total_municipalities": len(municipalities_out),
            "audited_municipalities": sum(1 for m in municipalities_out if m["audit_status"] == "AUDITED"),
            "in_progress_municipalities": sum(1 for m in municipalities_out if m["audit_status"] == "IN_PROGRESS"),
            "total_facilities": len(flat_facilities),
            "verified_facilities": sum(1 for f in flat_facilities if f["verification_status"] == "verified"),
            "partially_verified_facilities": sum(1 for f in flat_facilities if f["verification_status"] == "partially_verified"),
            "facility_level_collection_sum": facility_level_collection_sum,
            "system_aggregate_collection_sum": system_aggregate_collection_sum,
            "total_sources": len(sources_list),
            "license": "CC BY 4.0"
        },
        "municipalities": municipalities_out,
        "facilities": flat_facilities,
        "sources": sources_list
    }

    with open(os.path.join(out_dir, "libraries.json"), "w", encoding="utf-8") as f:
        json.dump(dataset_payload, f, ensure_ascii=False, indent=2)

    # 3. CSV export
    csv_headers = [
        "facility_id", "municipality_code", "municipality_name", "municipality_name_en",
        "name", "name_en", "category", "legal_status", "postal_code", "address",
        "phone", "fax", "established_year_month", "opened_year_month",
        "building_structure", "floor_area_m2", "reading_seats",
        "statistics_scope", "fiscal_year", "basis_date", "collection_count", "annual_loans",
        "verification_status", "verified_at", "unverified_fields", "sources"
    ]
    with open(os.path.join(out_dir, "libraries.csv"), "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(csv_headers)
        for row in flat_facilities:
            writer.writerow([
                row["facility_id"], row["municipality_code"], row["municipality_name"], row["municipality_name_en"],
                row["name"], row["name_en"], row["category"], row["legal_status"],
                row["postal_code"] or "", row["address"] or "", row["phone"] or "", row["fax"] or "",
                row["established_year_month"] or "", row["opened_year_month"] or "",
                row["building_structure"] or "",
                row["floor_area_m2"] if row["floor_area_m2"] is not None else "",
                row["reading_seats"] if row["reading_seats"] is not None else "",
                row["statistics_scope"] or "",
                row["fiscal_year"] if row["fiscal_year"] is not None else "",
                row["basis_date"] or "",
                row["collection_count"] if row["collection_count"] is not None else "",
                row["annual_loans"] if row["annual_loans"] is not None else "",
                row["verification_status"] or "",
                row["verified_at"] or "",
                ";".join(row["unverified_fields"]),
                ";".join(row["sources"])
            ])

    # 4. Google My Maps CSV export
    mymaps_headers = [
        "Name", "Name_EN", "Municipality", "Category", "Legal_Status",
        "Address", "Phone", "Collection_Count", "Statistics_Scope", "Verification_Status", "Sources"
    ]
    with open(os.path.join(out_dir, "libraries_mymaps.csv"), "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(mymaps_headers)
        for row in flat_facilities:
            writer.writerow([
                row["name"], row["name_en"], row["municipality_name"],
                row["category"], row["legal_status"],
                f"茨城県{row['address']}" if row["address"] else f"茨城県{row['municipality_name']}",
                row["phone"] or "",
                row["collection_count"] if row["collection_count"] is not None else "",
                row["statistics_scope"] or "",
                row["verification_status"] or "",
                ", ".join(row["sources"])
            ])

    # 5. GeoJSON export (with explicit coordinate_verified flag = false when exact coordinates are not yet geocoded from primary survey)
    geojson_payload = {
        "type": "FeatureCollection",
        "metadata": {
            "title": "Ibaraki Public Libraries GeoJSON",
            "note": "Exact lat/lon coordinates are not guessed; geometry is null until primary geocoding verification is completed. Use address attributes for geocoding.",
            "total_features": len(flat_facilities)
        },
        "features": [
            {
                "type": "Feature",
                "id": row["facility_id"],
                "geometry": None,
                "properties": {
                    "facility_id": row["facility_id"],
                    "municipality_code": row["municipality_code"],
                    "municipality_name": row["municipality_name"],
                    "name": row["name"],
                    "name_en": row["name_en"],
                    "category": row["category"],
                    "legal_status": row["legal_status"],
                    "address": f"茨城県{row['address']}" if row["address"] else None,
                    "phone": row["phone"],
                    "collection_count": row["collection_count"],
                    "statistics_scope": row["statistics_scope"],
                    "verification_status": row["verification_status"],
                    "coordinate_verified": False,
                    "sources": row["sources"]
                }
            }
            for row in flat_facilities
        ]
    }
    with open(os.path.join(out_dir, "libraries.geojson"), "w", encoding="utf-8") as f:
        json.dump(geojson_payload, f, ensure_ascii=False, indent=2)

    print(f"Generated exports in {out_dir}: libraries.json, sources.json, libraries.csv, libraries_mymaps.csv, libraries.geojson")

if __name__ == "__main__":
    generate_exports()
