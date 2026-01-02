from src.core.models.state import State


class Tracker:
    """Optional tracker for extracting metrics from scratchpad reasoning."""

    def __init__(self):
        pass

    async def update(
        self, state: State, scratchpad: str, customer_response: str
    ) -> State:
        """Update state metadata based on scratchpad analysis."""
        return state

    def to_xml(self, state: State) -> str:
        """Convert tracker state to <METRICS> XML format for agent prompts."""
        metadata = state.metadata
        xml = "<METRICS>\n"

        for key, value in metadata.items():
            xml += f"  <{key}>{value}</{key}>\n"

        xml += "</METRICS>"
        return xml
