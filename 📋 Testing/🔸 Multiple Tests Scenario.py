top_device_configs = [
    {
        "product_name": "Apple iPhone 17 Pro Max",
        "category": "smartphone",
        "region": "US",
        "reporting_currency": "USD",
        "purchase_price": 5900.0,
        "purchase_currency": "CNY",
        "volume_units": 12000,
        "current_or_planned_price": 1199.0,
        "target_margin_pct": 0.22,
        "manager_notes": "Текущий флагман Apple для power users; высокий спрос в сезон праздников и при старте продаж.",
        "user_id": "orchestrator-top-1-iphone17promax",
    },
    {
        "product_name": "Samsung Galaxy S25 Ultra",
        "category": "smartphone",
        "region": "US",
        "reporting_currency": "USD",
        "purchase_price": 5600.0,
        "purchase_currency": "CNY",
        "volume_units": 9000,
        "current_or_planned_price": 1299.99,
        "target_margin_pct": 0.25,
        "manager_notes": "Android-флагман с упором на камеру и AI; конкурирует с iPhone Pro Max в премиум-сегменте.",
        "user_id": "orchestrator-top-2-galaxys25ultra",
    },
    # ...
    # ...
    # ...
]



import json
all_orchestrator_results = []
evaluation_results = []


def _compute_derived_metrics(brief_text: str,
                             structured_summary,
                             evaluation_obj: dict) -> dict:
    brief = brief_text or ""
    struct = structured_summary or {}
    dims = evaluation_obj.get("dimensions") or {}

    length_chars = len(brief)
    length_words = len(brief.split())

    has_bullets = any(mark in brief for mark in ["- ", "• ", "* "])
    has_numbered = any(mark in brief for mark in ["1.", "2.", "3."])
    has_sections = any(h in brief.lower() for h in ["summary", "recommendation", "risk", "scenario"])

    structure_flags = [has_bullets, has_numbered, has_sections]
    structure_score = sum(1 for f in structure_flags if f) / max(len(structure_flags), 1)

    if isinstance(struct, str):
        try:
            struct_obj = json.loads(struct)
        except Exception:
            struct_obj = {}
    else:
        struct_obj = struct if isinstance(struct, dict) else {}

    required_keys = [
        "recommended_price",
        "target_margin_pct",
        "fx_risk_level",
        "scenario_analysis",
        "confidence_score",
    ]
    present_keys = [k for k in required_keys if k in struct_obj]
    json_completeness = len(present_keys) / max(len(required_keys), 1)

    coverage = dims.get("coverage")
    consistency = dims.get("consistency")
    clarity = dims.get("clarity")
    actionability = dims.get("actionability")

    components = [
        v for v in [
            coverage,
            consistency,
            clarity,
            actionability,
            structure_score,
            json_completeness,
        ]
        if isinstance(v, (int, float))
    ]
    quality_score = sum(components) / max(len(components), 1) if components else None

    return {
        "length_chars": length_chars,
        "length_words": length_words,
        "structure_score": structure_score,
        "json_completeness": json_completeness,
        "quality_score": quality_score,
        "has_bullets": has_bullets,
        "has_numbered_list": has_numbered,
        "has_named_sections": has_sections,
        "present_structured_keys": present_keys,
    }



#                               [from:to]
configs_to_run = top_device_configs[1:100]

for idx, cfg in enumerate(configs_to_run, start=1):
    print("\n\n" + "=" * 80)
    print(f"DEVICE {idx}/{len(top_device_configs)}: {cfg['product_name']} ({cfg['region']})")
    print("=" * 80 + "\n")

    run_result = await test_fx_pricing_orchestrator_once(cfg)
    all_orchestrator_results.append(run_result)

    brief = run_result["result"]["decision_brief_text"]
    structured = run_result["result"]["structured_summary_json"]
    evaluation_raw = run_result["result"]["evaluation_json"]

    if isinstance(evaluation_raw, str):
        try:
            evaluation_obj = json.loads(evaluation_raw)
        except Exception:
            evaluation_obj = {"raw": evaluation_raw}
    else:
        evaluation_obj = evaluation_raw

    derived_metrics = _compute_derived_metrics(
        brief_text=brief,
        structured_summary=structured,
        evaluation_obj=evaluation_obj or {},
    )

    evaluation_results.append(
        {
            "index": idx,
            "config": {
                "product_name": cfg.get("product_name"),
                "region": cfg.get("region"),
                "target_margin_pct": cfg.get("target_margin_pct"),
            },
            "overall_score": evaluation_obj.get("overall_score") if isinstance(evaluation_obj, dict) else None,
            "dimensions": evaluation_obj.get("dimensions") if isinstance(evaluation_obj, dict) else None,
            "flags": evaluation_obj.get("flags") if isinstance(evaluation_obj, dict) else None,
            "summary_comment": evaluation_obj.get("summary_comment") if isinstance(evaluation_obj, dict) else None,
            "derived_metrics": derived_metrics,
            "full": evaluation_obj,
        }
    )
    # i lowered the character limit specifically to avoid cluttering it with too much text
    
    print("=== Decision brief (first 300 chars) ===")
    print(brief[:300])
    print("\n=== Structured summary JSON (first 300 chars) ===")
    print(structured[:300])
    print("\n=== Evaluation JSON (first 300 chars) ===")
    eval_str = evaluation_raw if isinstance(evaluation_raw, str) else json.dumps(evaluation_obj, indent=2)
    print(eval_str[:300])
    print("\n=== Observability summary ===")
    print(run_result["observability_summary"])
    print("\n=== Basic health ===")
    print(run_result["health_basic"])

print("\n✅ Top-device orchestrator tests finished.")
print(f"Stored runs: {len(all_orchestrator_results)}")
print(f"Stored evaluation records: {len(evaluation_results)}")
