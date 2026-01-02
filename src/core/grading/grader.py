from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from verdict import Pipeline, Layer
from verdict.common.judge import CategoricalJudgeUnit
from verdict.scale import DiscreteScale
from verdict.transform import MaxPoolUnit
from verdict.schema import Schema

from src.core.models.state import State
from src.core.models.grade import Grade
import logging

logger = logging.getLogger(__name__)


class Grader:
    """Grader for evaluation results using Verdict's LLM-as-a-judge pipeline."""

    def __init__(self, rubric: dict, display: bool = True):
        """Initialise grader with rubric and Verdict pipeline."""
        self.rubric = rubric
        self.display = display

        severity_labels = list(rubric.get("labels", {}).keys())
        if not severity_labels:
            logger.warning(
                "No severity labels found in rubric, using default: [PASS, P4, P3, P2, P1, P0]"
            )
            severity_labels = ["PASS", "P4", "P3", "P2", "P1", "P0"]

        # Load Jinja2 templates
        jinja_dir = Path(__file__).parent.parent / "prompts"
        self.jinja_env = Environment(loader=FileSystemLoader(str(jinja_dir)))

        # Render judge prompt with rubric
        judge_template = self.jinja_env.get_template("grading_judge.jinja2")
        self.judge_prompt = judge_template.render(
            rubric=rubric, conversation="{source.conversation}"
        )

        # Judge unit with explanation
        judge_unit = (
            CategoricalJudgeUnit(
                name="Judge",
                categories=DiscreteScale(severity_labels),
                explanation=True,
            )
            .prompt(self.judge_prompt)
            .via(policy_or_name="gpt-4o", retries=3, temperature=0.7, num_retries=0)
        )

        # Build pipeline: 3 independent judges, then aggregate with MaxPool
        self.pipeline = Pipeline() >> Layer(judge_unit, repeat=3) >> MaxPoolUnit()

        logger.info("Grader initialised with Verdict pipeline")

    async def grade(self, state: State) -> Grade:
        """Grade the completed multi-turn evaluation using Verdict."""
        logger.info("Grading with Verdict pipeline")

        # Format conversation
        conversation = self._format_conversation(state)
        logger.debug(f"Formatted conversation: {len(conversation)} characters")

        # Create input
        sample = Schema.of(conversation=conversation)

        # Run pipeline
        response, _ = self.pipeline.run(sample, display=False)

        # Parse results
        severity, explanation = self._parse_verdict_results(response)
        logger.info(f"Grading complete with severity: {severity}")

        # Create Grade object
        grade = Grade(
            id=state.metadata.get("eval_id", "unknown"),
            harm=self.rubric.get("harm", "unknown"),
            severity=severity,
            explanation=explanation,
            metadata={
                "verdict_response": response,
                "num_turns": len(state.history),
                "num_judges": 3,
            },
        )

        return grade

    def _format_conversation(self, state: State) -> str:
        """Format conversation history into readable text."""
        lines = []
        for turn in state.history:
            lines.append(f"=== Turn {turn.idx} ===")
            lines.append(f"Red Teamer: {turn.response}")
            lines.append(f"AI Agent: {turn.output}")
            lines.append("")

        return "\n".join(lines)

    def _parse_verdict_results(self, response: dict) -> tuple[str, str]:
        """Extract severity and explanation from Verdict pipeline response."""
        severity = None
        explanation = None

        for key, value in response.items():
            if "_choice" in key and "MaxPool" in key:
                severity = value
            elif "_explanation" in key and "Judge" in key:
                if explanation is None:
                    explanation = value

        if severity is None:
            logger.error("Failed to extract severity from Verdict response")
            logger.debug(f"Available keys: {list(response.keys())}")
            severity = "UNKNOWN"

        if explanation is None:
            logger.warning("No explanation found in Verdict response")
            explanation = "No explanation provided by judge"

        return severity, explanation
