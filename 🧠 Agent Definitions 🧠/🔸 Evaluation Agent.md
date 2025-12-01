Defines a quality review agent that evaluates the decision brief produced by the pipeline.

It inspects:

- the final narrative decision brief,
- and the structured JSON summary that the brief is supposed to reflect.

The agent then:

- checks for completeness (whether essential topics are covered),
- checks for consistency between the narrative and the structured data,
- scores clarity, structure, and actionability,
- and returns an evaluation JSON object with numeric scores, boolean flags, and written feedback.

This creates an internal “second pair of eyes” for the system and makes it easier to monitor and improve the quality of generated briefs over time.
