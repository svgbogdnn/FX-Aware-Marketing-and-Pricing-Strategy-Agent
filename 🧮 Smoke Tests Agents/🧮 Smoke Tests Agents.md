Runs lightweight smoke tests for each specialist agent in the FX-aware pricing system.

The tests:

- execute every agent independently (market research, competitive pricing, vendor FX, FX impact, margin planner, decision brief and evaluation) using small synthetic inputs;
- route each prompt through the standard `InMemoryRunner` and session service to exercise the same execution path as in the main pipeline;
- collect the textual response from the streaming events and print only the first `MAX_PREVIEW_CHARS` characters (set to 300) for each agent, because the full outputs are often very long and would otherwise flood the notebook output;
- separate agents visually with clear headers and separators, making it easy to see which agent produced which preview.

To see the full output for a given agent, it is enough to adjust the truncation in this cell — for example, by increasing `MAX_PREVIEW_CHARS` or by removing the `[:MAX_PREVIEW_CHARS]` slice on `full_text` in the corresponding `print` call.

For reviewers who prefer not to change the code, a complete, untruncated sample output of this smoke-test cell is also available here for reference:  
https://drive.google.com/file/d/18Tl78qd-mKnYCkDadrmJesgC-KhTxNyZ/view?usp=sharing
