import os
import re
import sys
import glob
import json

def verify_markdown_cross_reference(text):
    """
    Verifies that all citations [1], [2] in the body match entries in the References section,
    and all entries in References are cited in the body.
    """
    ref_heading_match = re.search(r'(?m)^#+\s*References[^\n]*', text)
    if not ref_heading_match:
        return {
            "status": "fail",
            "error": "References section heading not found in text."
        }

    body = text[:ref_heading_match.start()]
    references_section = text[ref_heading_match.start():]

    # Avoid matching citations inside fenced code blocks
    body_without_code = re.sub(r'```.*?```', '', body, flags=re.DOTALL)

    # Citations are [digits] not immediately followed by (
    body_citations = re.findall(r'\[(\d+)\](?!\()', body_without_code)
    body_citations_set = set(int(x) for x in body_citations)

    # Entries in references section: e.g. - [1] or * [1] or 1. [1]
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
    if not ref_entries_set:
        status = "fail"
        errors.append("References欄に有効な参照項目が存在しません。")
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


def run_self_test():
    """
    Runs unit tests on verify_markdown_cross_reference to ensure both positive
    and negative cases are accurately detected.
    """
    tests = [
        (
            "valid_doc",
            "Fact A[1] and Fact B[1][2].\n\n### References（参考文献・参照資料）\n- [1] Source 1\n- [2] Source 2\n",
            "pass"
        ),
        (
            "missing_heading",
            "Fact A[1].\n- [1] Source 1\n",
            "fail"
        ),
        (
            "dangling_citation",
            "Fact A[1] and Fact B[3].\n\n### References\n- [1] Source 1\n- [2] Source 2\n",
            "fail"
        ),
        (
            "unused_reference",
            "Fact A[1].\n\n### References\n- [1] Source 1\n- [2] Source 2\n",
            "fail"
        ),
        (
            "non_sequential_reference",
            "Fact A[1] and Fact B[3].\n\n### References\n- [1] Source 1\n- [3] Source 3\n",
            "fail"
        )
    ]
    failures = []
    for name, sample, expected in tests:
        res = verify_markdown_cross_reference(sample)
        if res["status"] != expected:
            failures.append({"test": name, "expected": expected, "actual": res["status"], "res": res})

    return {
        "status": "pass" if not failures else "fail",
        "tests_run": len(tests),
        "failures": failures
    }


def main():
    args = sys.argv[1:]
    if not args:
        print(json.dumps({"status": "fail", "error": "No target files or --self-test specified."}, ensure_ascii=False, indent=2))
        sys.exit(1)

    if "--self-test" in args:
        st_res = run_self_test()
        print(json.dumps(st_res, ensure_ascii=False, indent=2))
        if st_res["status"] != "pass":
            sys.exit(1)
        args = [a for a in args if a != "--self-test"]
        if not args:
            sys.exit(0)

    target_files = []
    for arg in args:
        if os.path.isdir(arg):
            md_files = sorted(glob.glob(os.path.join(arg, "**", "*.md"), recursive=True))
            target_files.extend(md_files)
        elif os.path.isfile(arg):
            target_files.append(arg)
        else:
            print(json.dumps({"status": "fail", "error": f"Target path not found: {arg}"}, ensure_ascii=False, indent=2))
            sys.exit(1)

    if not target_files:
        print(json.dumps({"status": "fail", "error": "No markdown files found in specified paths."}, ensure_ascii=False, indent=2))
        sys.exit(1)

    overall_status = "pass"
    results = {}
    for tf in target_files:
        with open(tf, "r", encoding="utf-8") as f:
            content = f.read()
        res = verify_markdown_cross_reference(content)
        results[tf] = res
        if res["status"] != "pass":
            overall_status = "fail"

    output = {
        "status": overall_status,
        "files_checked": len(target_files),
        "results": results
    } if len(target_files) > 1 else results[target_files[0]]

    print(json.dumps(output, ensure_ascii=False, indent=2))
    sys.exit(0 if overall_status == "pass" else 1)


if __name__ == "__main__":
    main()
