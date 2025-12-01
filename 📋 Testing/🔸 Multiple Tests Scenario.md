Prepares a large-scale multi-device test scenario where the FX-aware pricing orchestrator is run over a **portfolio of 1,000 products**, and the results are collected for comparison and evaluation.

- `top_device_configs` defines a portfolio of up to 1,000 realistic device configurations with purchase costs, volumes, target margins, manager notes and `user_id`s.
- The loop (when un-commented) iterates over this portfolio and, for each device:
  - calls `test_fx_pricing_orchestrator_once(cfg)` to run the full end-to-end pipeline;
  - collects the raw result and appends it to `all_orchestrator_results`;
  - extracts the **decision brief**, **structured_summary_json** and **evaluation_json** and converts the evaluation into a Python object when possible;
  - computes additional derived metrics via `_compute_derived_metrics(...)` and appends them to `evaluation_results`.
- To keep the notebook output readable even at this scale, only the first 300 characters of each major text block are printed for each device, followed by the full observability summary and basic health indicators.

Full, untruncated logs for the **1,000-device run** are exported separately and can be inspected here:  
https://drive.google.com/file/d/1IypbQLG8Juxso--_VI8RMkudn6w8_UgW/view?usp=sharing

This scenario turns the notebook into a portfolio-level regression harness: it shows how the orchestrator behaves under a substantial, realistic workload of 1,000 devices and how its outputs can be aggregated into metrics suitable for cross-device comparison, robustness checks and later evaluation.
