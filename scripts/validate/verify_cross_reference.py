import re
import sys

def verify_markdown_cross_reference(text):
    """
    Verifies that all citations [1], [2] in the body match entries in the References section,
    and all entries in References are cited in the body.
    """
    # Split text into body and references section
    ref_heading_match = re.search(r'(?m)^#+\s*References[^\n]*', text)
    if not ref_heading_match:
        return {
            "status": "fail",
            "error": "References section heading not found in text."
        }

    body = text[:ref_heading_match.start()]
    references_section = text[ref_heading_match.start():]

    # Find citations in body: e.g. [1], [2], [1][2], etc.
    # Avoid matching markdown links like [title](url)
    # Citations are [digits] not immediately followed by (
    body_citations = re.findall(r'\[(\d+)\](?!\()', body)
    body_citations_set = set(int(x) for x in body_citations)

    # Find entries in references section:
    # e.g. - **[1]** or * **[1]** or - [1] or 1. [1]
    ref_entries = re.findall(r'(?m)^\s*[\*\-\d\.]+\s*(?:\*\*)?\[(\d+)\](?:\*\*)?', references_section)
    ref_entries_set = set(int(x) for x in ref_entries)

    dangling_in_body = body_citations_set - ref_entries_set
    unused_in_references = ref_entries_set - body_citations_set

    is_sequential = False
    if ref_entries_set:
        sorted_refs = sorted(list(ref_entries_set))
        is_sequential = (sorted_refs == list(range(1, max(sorted_refs) + 1)))

    status = "pass"
    errors = []
    if dangling_in_body:
        status = "fail"
        errors.append(f"本文中にReferencesに存在しない参照番号があります: {sorted(list(dangling_in_body))}")
    if unused_in_references:
        status = "fail"
        errors.append(f"References欄に本文で一度も参照されていない資料があります: {sorted(list(unused_in_references))}")
    if not is_sequential:
        status = "fail"
        errors.append(f"Referencesの番号が連番になっていません: {sorted(list(ref_entries_set))}")

    return {
        "status": status,
        "body_citations_count": len(body_citations),
        "unique_body_citations": sorted(list(body_citations_set)),
        "references_count": len(ref_entries),
        "unique_references": sorted(list(ref_entries_set)),
        "is_sequential": is_sequential,
        "errors": errors
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            content = f.read()
        res = verify_markdown_cross_reference(content)
        import json
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(0 if res["status"] == "pass" else 1)
