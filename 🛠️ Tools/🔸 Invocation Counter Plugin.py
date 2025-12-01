'''
Here we define reusable tools and utilities that support the FX-aware pricing agent.
They cover three main areas:

Domain tools for generating structured product, pricing and FX scenarios.
Operational tools for conversation management, configuration, batch runs and summarization.
Monitoring tools for feedback, quality checks and performance tracking.
Together, these tools give the agents a stable, inspectable environment and make the system easier to debug, evaluate and iterate on.
'''
from google.adk.plugins.logging_plugin import LoggingPlugin

class InvocationCounterPlugin(LoggingPlugin):
    """Logging plugin that counts model, tool, and agent invocations during runs"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_invocations = 0
        self.tool_invocations = 0
        self.agent_invocations = 0

    async def before_model_callback(self, *args, **kwargs):
        self.model_invocations += 1
        if hasattr(super(), "before_model_callback"):
            await super().before_model_callback(*args, **kwargs)

    async def before_tool_callback(self, *args, **kwargs):
        self.tool_invocations += 1
        if hasattr(super(), "before_tool_callback"):
            await super().before_tool_callback(*args, **kwargs)

    async def before_agent_callback(self, *args, **kwargs):
        self.agent_invocations += 1
        if hasattr(super(), "before_agent_callback"):
            await super().before_agent_callback(*args, **kwargs)

print("✔️ InvocationCounterPlugin has been installed!")
