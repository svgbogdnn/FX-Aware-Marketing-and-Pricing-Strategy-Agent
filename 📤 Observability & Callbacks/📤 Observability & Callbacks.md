Extends the base logging plugin with FX-specific observability.

The plugin captures:

- structured log events for key pipeline milestones,
- timing information for model, tool and agent calls,
- and a compact snapshot of configuration and runtime metadata.

Logs are stored in a machine-readable format so they can be inspected directly in the notebook, exported to JSON, or fed into external monitoring and evaluation workflows.  
This makes the agent’s behavior transparent and easier to debug or explain.
