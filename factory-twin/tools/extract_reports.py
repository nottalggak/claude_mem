"""서브에이전트 트랜스크립트(JSONL)에서 SubagentHandback 최종 보고서 본문만 추출해 docs/research/ 에 저장."""
import json, sys, pathlib
TASKS = pathlib.Path("/tmp/claude-0/-home-user-claude-mem/508c8abb-4a55-5c43-94f1-9a63dde73d06/tasks")
OUT = pathlib.Path(__file__).resolve().parent.parent / "docs/research"
NAMES = {
    "ac9504a4eac4fd20c": "01_digital_twin_platform_stack.md",
    "ad01732157cfa70f8": "02_onsite_capture_methods.md",
    "ab4769fe3021da4dd": "03_furniture_factory_process_domain.md",
    "ad1548ea0ce1ac927": "04_scan_to_3d_browser_pipeline.md",
    "afc5504492a834bca": "05_korea_smart_factory_ax_market.md",
    "a5bd004691830dd0e": "06_open_source_repos_shortlist.md",
}
OUT.mkdir(parents=True, exist_ok=True)
for aid, name in NAMES.items():
    f = TASKS / f"{aid}.output"
    if not f.exists():
        print("missing", aid); continue
    report = None
    for line in open(f, encoding="utf-8"):
        try: o = json.loads(line)
        except Exception: continue
        m = o.get("message") or {}
        for b in (m.get("content") or []) if isinstance(m.get("content"), list) else []:
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "SubagentHandback":
                inp = b.get("input") or {}
                report = inp.get("report") or inp.get("content") or inp.get("message") or json.dumps(inp, ensure_ascii=False)
    if report:
        (OUT / name).write_text(report, encoding="utf-8"); print("wrote", name, len(report))
    else:
        print("no handback yet:", aid)
