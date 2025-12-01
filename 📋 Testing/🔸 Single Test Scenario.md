Defines fully specified FX pricing scenario for single example and wires it to the orchestrator test harness.

- `single_test_config` describes one realistic launch scenario (product, category, region, currencies, volume, current price, target margin, manager notes, `user_id`).
- The code (when un-commented) runs `test_fx_pricing_orchestrator_once(single_test_config)` and prints a focused view of the most important outputs:
  - the natural-language **decision brief**,
  - the **structured_summary_json**,
  - the **evaluation_json** produced by the evaluation tool,
  - the **observability summary** and the basic health indicator.
- To keep the notebook readable and avoid flooding the output with low-level logs, only a compact subset of the information is shown inline; the full run with detailed logging is exported separately and can be inspected here:
  - full output for this scenario (all logs)
    https://drive.google.com/file/d/1CbD9OTg1Qna1IL990YlHFWXbrGuMno-V/view?usp=sharing.
