import os
import re
import sys
import json
import glob

def parse_simple_yaml(filepath):
    """
    Lightweight parser for our canonical YAML structure using only Python standard library,
    ensuring zero external dependency failures in both sandbox VMs and GitHub Actions.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    doc = {
        "municipality_code": None,
        "municipality_name": None,
        "municipality_name_en": None,
        "audit_status": None,
        "notes": None,
        "uninvestigated_or_excluded_facilities": None,
        "facilities": []
    }

    def unquote(val_str):
        val_str = val_str.strip()
        if val_str == "null" or val_str == "":
            return None
        if val_str == "[]":
            return []
        if val_str == "true":
            return True
        if val_str == "false":
            return False
        if (val_str.startswith('"') and val_str.endswith('"')) or (val_str.startswith("'") and val_str.endswith("'")):
            return json.loads(val_str) if val_str.startswith('"') else val_str[1:-1]
        try:
            if "." in val_str:
                return float(val_str)
            return int(val_str)
        except ValueError:
            return val_str

    current_fac = None
    current_section = None
    current_subsection = None

    for raw_line in lines:
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 0:
            if ":" in line:
                k, v = line.split(":", 1)
                if k.strip() != "facilities":
                    doc[k.strip()] = unquote(v)
        elif indent == 2 and line.startswith("- facility_id:"):
            if current_fac is not None:
                doc["facilities"].append(current_fac)
            _, v = line.split(":", 1)
            current_fac = {
                "facility_id": unquote(v),
                "statistics": {},
                "history": [],
                "sources": [],
                "field_sources": {},
                "verification": {"unverified_fields": []}
            }
            current_section = None
            current_subsection = None
        elif indent == 4 and current_fac is not None:
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip()
                v_str = v.strip()
                if k in ("statistics", "history", "sources", "field_sources", "verification"):
                    current_section = k
                    current_subsection = None
                    if v_str == "[]":
                        current_fac[k] = []
                else:
                    current_fac[k] = unquote(v_str)
                    current_section = None
        elif indent == 6 and current_fac is not None:
            if current_section == "sources" and line.startswith("- "):
                current_fac["sources"].append(unquote(line[2:]))
            elif current_section == "history":
                if line == "[]":
                    pass
                elif line.startswith("- date:"):
                    _, v = line.split(":", 1)
                    current_fac["history"].append({"date": unquote(v), "event": None})
            elif current_section == "statistics" and ":" in line:
                k, v = line.split(":", 1)
                k = k.strip()
                if k == "breakdown":
                    if unquote(v) is None:
                        current_fac["statistics"]["breakdown"] = None
                        current_subsection = None
                    else:
                        current_fac["statistics"]["breakdown"] = {}
                        current_subsection = "breakdown"
                else:
                    current_fac["statistics"][k] = unquote(v)
                    current_subsection = None
            elif current_section == "field_sources" and ":" in line:
                k, v = line.split(":", 1)
                current_fac["field_sources"][k.strip()] = unquote(v)
            elif current_section == "verification" and ":" in line:
                k, v = line.split(":", 1)
                k = k.strip()
                if k == "unverified_fields":
                    if v.strip() == "[]":
                        current_fac["verification"]["unverified_fields"] = []
                        current_subsection = None
                    else:
                        current_subsection = "unverified_fields"
                else:
                    current_fac["verification"][k] = unquote(v)
                    current_subsection = None
        elif indent == 8 and current_fac is not None:
            if current_section == "history" and line.startswith("event:") and current_fac["history"]:
                _, v = line.split(":", 1)
                current_fac["history"][-1]["event"] = unquote(v)
            elif current_section == "statistics" and current_subsection == "breakdown" and ":" in line:
                k, v = line.split(":", 1)
                current_fac["statistics"]["breakdown"][k.strip()] = unquote(v)
            elif current_section == "verification" and current_subsection == "unverified_fields" and line.startswith("- "):
                current_fac["verification"]["unverified_fields"].append(unquote(line[2:]))

    if current_fac is not None:
        doc["facilities"].append(current_fac)

    return doc


def parse_source_yaml(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    sid_m = re.search(r'source_id:\s*"([^"]+)"', text)
    url_m = re.search(r'url:\s*"([^"]+)"', text)
    acc_m = re.search(r'accessed_date:\s*"([^"]+)"', text)
    st_m = re.search(r'status:\s*"([^"]+)"', text)
    vat_m = re.search(r'verified_at:\s*"([^"]+)"', text)
    return {
        "source_id": sid_m.group(1) if sid_m else None,
        "url": url_m.group(1) if url_m else None,
        "accessed_date": acc_m.group(1) if acc_m else None,
        "status": st_m.group(1) if st_m else None,
        "verified_at": vat_m.group(1) if vat_m else None
    }


def validate_all_canonical_data(repo_root=None):
    if repo_root is None:
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    master_path = os.path.join(repo_root, "data", "municipalities", "master_municipalities.json")
    with open(master_path, "r", encoding="utf-8") as f:
        master = json.load(f)

    # 1. Load all sources
    source_files = sorted(glob.glob(os.path.join(repo_root, "data", "sources", "SRC-*.yaml")))
    sources_map = {}
    errors = []

    for sf in source_files:
        sdata = parse_source_yaml(sf)
        sid = sdata["source_id"]
        if not sid:
            errors.append(f"Source file missing source_id: {sf}")
            continue
        if not sdata["url"] or not sdata["accessed_date"] or sdata["status"] != "verified" or not sdata["verified_at"]:
            errors.append(f"Source {sid} has incomplete verification metadata: {sdata}")
        sources_map[sid] = sdata

    # 2. Load and validate all 44 municipality YAMLs
    yaml_files = sorted(glob.glob(os.path.join(repo_root, "data", "libraries", "*.yaml")))
    if len(yaml_files) != 44:
        errors.append(f"Expected 44 municipality YAML files, found {len(yaml_files)}")

    seen_codes = set()
    seen_facility_ids = set()
    total_facilities = 0
    verified_facilities = 0
    partially_verified_facilities = 0
    category_counts = {"Cat A": 0, "Cat B": 0, "Cat C": 0, "Cat D": 0}
    scope_counts = {"facility_level": 0, "system_aggregate": 0, "not_applicable": 0}

    valid_categories = {"Cat A", "Cat B", "Cat C", "Cat D"}
    valid_legal_statuses = {
        "central_library", "branch_library", "branch_room",
        "branch_collection", "community_center_library",
        "annex_facility", "service_point"
    }
    valid_scopes = {"facility_level", "system_aggregate", "not_applicable"}

    for yf in yaml_files:
        doc = parse_simple_yaml(yf)
        fname = os.path.basename(yf)
        code = doc["municipality_code"]
        name_ja = doc["municipality_name"]

        if code not in master:
            errors.append(f"{fname}: Invalid municipality_code '{code}'")
            continue
        if master[code]["name_ja"] != name_ja:
            errors.append(f"{fname}: Municipality name '{name_ja}' does not match master '{master[code]['name_ja']}'")
        seen_codes.add(code)

        if not doc.get("uninvestigated_or_excluded_facilities"):
            errors.append(f"{fname}: Missing 'uninvestigated_or_excluded_facilities' disclosure")

        facs = doc.get("facilities", [])
        if not facs:
            errors.append(f"{fname}: No facilities listed")

        for idx, fac in enumerate(facs, start=1):
            total_facilities += 1
            fid = fac.get("facility_id")
            expected_fid = f"IB-{code}-{idx:02d}"
            if fid != expected_fid:
                errors.append(f"{fname}: Facility ID '{fid}' does not match expected '{expected_fid}'")
            if fid in seen_facility_ids:
                errors.append(f"{fname}: Duplicate facility_id '{fid}'")
            seen_facility_ids.add(fid)

            cat = fac.get("category")
            if cat not in valid_categories:
                errors.append(f"{fname} ({fid}): Invalid category '{cat}'")
            else:
                category_counts[cat] += 1

            lstatus = fac.get("legal_status")
            if lstatus not in valid_legal_statuses:
                errors.append(f"{fname} ({fid}): Invalid legal_status '{lstatus}'")

            # Check statistics block
            stats = fac.get("statistics", {})
            scope = stats.get("scope")
            if scope not in valid_scopes:
                errors.append(f"{fname} ({fid}): Invalid statistics.scope '{scope}'")
            else:
                scope_counts[scope] += 1

            col = stats.get("collection_count")
            if scope in ("facility_level", "system_aggregate"):
                if col is None or not isinstance(col, int) or col <= 0:
                    errors.append(f"{fname} ({fid}): scope='{scope}' requires positive integer collection_count, got {col}")
                if stats.get("fiscal_year") != 2024 or stats.get("basis_date") != "2025-03-31":
                    errors.append(f"{fname} ({fid}): Inconsistent fiscal_year/basis_date in statistics")

            # Check sources & field_sources
            f_sources = fac.get("sources", [])
            if not f_sources:
                errors.append(f"{fname} ({fid}): Empty sources list")
            for s_id in f_sources:
                if s_id not in sources_map:
                    errors.append(f"{fname} ({fid}): Referenced source '{s_id}' does not exist in data/sources/")

            fld_sources = fac.get("field_sources", {})
            for req_key in ("identity_and_location", "legal_basis", "building_and_capacity", "statistics"):
                if req_key not in fld_sources or not fld_sources[req_key]:
                    errors.append(f"{fname} ({fid}): Missing field_sources.{req_key}")

            # Check verification status vs unverified fields
            ver = fac.get("verification", {})
            v_status = ver.get("status")
            unv_list = ver.get("unverified_fields", [])

            has_unverified_field_source = any("unverified" in str(v) for v in fld_sources.values())
            has_null_core = (
                fac.get("address") is None or
                fac.get("established_year_month") is None or
                fac.get("floor_area_m2") is None or
                (cat == "Cat A" and lstatus in ("central_library", "branch_library") and fac.get("reading_seats") is None and scope != "not_applicable")
            )

            if v_status == "verified":
                verified_facilities += 1
                if unv_list or has_unverified_field_source or has_null_core:
                    errors.append(
                        f"{fname} ({fid}): Marked as 'verified' despite having unverified/null core fields "
                        f"(unv_list={unv_list}, has_unverified_field_source={has_unverified_field_source}, has_null_core={has_null_core})"
                    )
            elif v_status == "partially_verified":
                partially_verified_facilities += 1
                if not unv_list:
                    errors.append(f"{fname} ({fid}): Marked as 'partially_verified' but unverified_fields list is empty")
            else:
                errors.append(f"{fname} ({fid}): Invalid verification.status '{v_status}'")

    missing_codes = set(master.keys()) - seen_codes
    if missing_codes:
        errors.append(f"Missing municipality YAML files for codes: {sorted(missing_codes)}")

    result = {
        "status": "pass" if not errors else "fail",
        "municipalities_checked": len(seen_codes),
        "total_facilities_checked": total_facilities,
        "verified_facilities": verified_facilities,
        "partially_verified_facilities": partially_verified_facilities,
        "category_counts": category_counts,
        "statistics_scope_counts": scope_counts,
        "registered_sources_count": len(sources_map),
        "errors": errors
    }
    return result

if __name__ == "__main__":
    res = validate_all_canonical_data()
    print(json.dumps(res, ensure_ascii=False, indent=2))
    sys.exit(0 if res["status"] == "pass" else 1)
