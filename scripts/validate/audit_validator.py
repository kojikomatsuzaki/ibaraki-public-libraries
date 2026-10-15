import os
import json
import sys

def run_validation(repo_root=None):
    if repo_root is None:
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    master_path = os.path.join(repo_root, "data", "municipalities", "master_municipalities.json")
    registry_path = os.path.join(repo_root, "data", "municipalities", "audit_registry.json")

    with open(master_path, "r", encoding="utf-8") as f:
        master = json.load(f)

    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    master_keys = set(master.keys())
    registry_keys = set(registry.keys())

    missing_in_registry = master_keys - registry_keys
    unexpected_in_registry = registry_keys - master_keys

    errors = []
    if missing_in_registry:
        missing_names = [f"{k}({master[k]['name_ja']})" for k in sorted(missing_in_registry)]
        errors.append(f"欠落自治体検出 ({len(missing_in_registry)}件): {', '.join(missing_names)}")
    if unexpected_in_registry:
        errors.append(f"未定義エンティティ混入 ({len(unexpected_in_registry)}件): {', '.join(sorted(unexpected_in_registry))}")

    status_counts = {"AUDITED": 0, "IN_PROGRESS": 0, "NOT_STARTED": 0}
    reclassified_as_in_progress = []

    for code in sorted(master.keys()):
        data = registry.get(code, {})
        claimed_status = data.get("status", "NOT_STARTED")
        pillars = data.get("pillars", {})
        has_legal = bool(pillars.get("legal", {}).get("url") and pillars.get("legal", {}).get("title"))
        has_facility = bool(pillars.get("facility", {}).get("url"))
        has_stats = bool(pillars.get("statistics", {}).get("url") and pillars.get("statistics", {}).get("fiscal_year"))

        final_status = claimed_status
        if claimed_status == "AUDITED":
            if not (has_legal and has_facility and has_stats):
                final_status = "IN_PROGRESS"
                reclassified_as_in_progress.append({
                    "code": code,
                    "name": master[code]["name_ja"],
                    "missing_pillars": [p for p, ok in [("法規系統", has_legal), ("施設系統", has_facility), ("統計系統", has_stats)] if not ok]
                })

        status_counts[final_status] += 1

    return {
        "status": "pass" if not errors else "fail",
        "master_count": len(master),
        "registry_count": len(registry),
        "errors": errors,
        "status_counts": status_counts,
        "reclassified_count": len(reclassified_as_in_progress)
    }

if __name__ == "__main__":
    res = run_validation()
    print(json.dumps(res, ensure_ascii=False, indent=2))
    sys.exit(0 if res["status"] == "pass" else 1)
