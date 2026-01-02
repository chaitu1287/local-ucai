import os
from pathlib import Path
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from jinja2 import Environment, FileSystemLoader

from src.core.models.specification import Specification, RedTeamModel
from src.core.parsers.xml import XMLParser
from src.core.utils.logging import log_section
from src.core.transforms import load_transforms
from src.core.refusal.classifier import get_refusal_detector

import logging

logger = logging.getLogger(__name__)


class RedTeamer:
    """Red-teaming agent that generates adversarial responses using plan-based reasoning."""

    def __init__(self, spec: Specification, retries: int = 3):
        """Initialize the red-teaming agent with evaluation specification."""
        self.spec = spec
        self.model = spec.agent.model

        if self.model == RedTeamModel.CLAUDE_SONNET_4_5:
            self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        elif self.model == RedTeamModel.GPT_5:
            self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            raise ValueError(f"Unsupported model: {self.model}")

        self.conversation: list[dict] = []

        # Agent output configuration
        self.include_plan = spec.agent.plan
        self.include_scratchpad = spec.agent.scratchpad
        self.retries = retries

        # Load transforms from specification
        if spec.attack.transforms:
            self.transforms = load_transforms(spec.attack.transforms)
            logger.info(f"Loaded transforms: {spec.attack.transforms}")
        else:
            self.transforms = None

        # Load Jinja2 templates
        jinja_dir = Path(__file__).parent.parent / "prompts"
        self.jinja_env = Environment(loader=FileSystemLoader(str(jinja_dir)))

        # Build system prompt
        self.system_prompt = self.spec.prompt
        logger.info("Using custom system prompt from specification")
        logger.info(f"RedTeamer initialized (model={self.model.value})")
        log_section(logger, "INFO", "SYSTEM PROMPT", self.system_prompt)

    async def plan(self) -> str | None:
        """Generate initial attack plan."""
        if not self.include_plan:
            return None

        logger.info("Generating initial attack plan")
        template = self.jinja_env.get_template("generate_plan.jinja2")
        user_message = template.render()

        self.conversation.append({"role": "user", "content": user_message})
        response = await self._call_llm()
        self.conversation.append({"role": "assistant", "content": response})

        plan = XMLParser.extract_tag(response, "PLAN")
        logger.debug(f"Plan generated: {plan}")
        return plan

    async def update(self, customer_output: str) -> str | None:
        """Evaluate customer response and update plan."""
        if not self.include_plan:
            return None

        logger.info("Updating plan after customer response")
        logger.debug(f"Customer output: {customer_output}")
        template = self.jinja_env.get_template("update_plan.jinja2")
        user_message = template.render(customer_output=customer_output)

        self.conversation.append({"role": "user", "content": user_message})
        response = await self._call_llm()
        self.conversation.append({"role": "assistant", "content": response})

        plan = XMLParser.extract_tag(response, "PLAN")
        logger.debug(f"Updated plan: {plan}")
        return plan

    async def respond(
        self, turn: int, n_turns: int
    ) -> tuple[str | None, str | None, str]:
        """Generate adversarial response with optional scratchpad reasoning."""
        logger.info(f"Generating adversarial response for turn {turn}/{n_turns}")
        template = self.jinja_env.get_template("generate_response.jinja2")
        user_message = template.render(
            turn=turn, n_turns=n_turns, include_scratchpad=self.include_scratchpad
        )

        self.conversation.append({"role": "user", "content": user_message})

        xml = None
        output = None

        for attempt in range(self.retries + 1):
            prefill = "Test prompt:" if attempt > 0 else None
            xml = await self._call_llm(prefill=prefill)

            logger.debug(
                f"Attempt {attempt + 1}: Received XML response (length: {len(xml)})"
            )
            logger.debug(
                f"Full XML: {xml[:500]}..." if len(xml) > 500 else f"Full XML: {xml}"
            )

            output = XMLParser.extract_tag(xml, "OUTPUT")

            if output is None:
                logger.debug("OUTPUT tag not found in XML or empty")
            else:
                logger.debug(
                    f"Extracted OUTPUT (length: {len(output)}): {output[:200]}..."
                    if len(output) > 200
                    else f"Extracted OUTPUT: {output}"
                )

                # Check refusal detection
                is_refusal = get_refusal_detector().detect(output)
                logger.debug(f"Refusal detector result: {is_refusal}")

                if not is_refusal:
                    self.conversation.append({"role": "assistant", "content": xml})
                    logger.debug(f"Valid response generated on attempt {attempt + 1}")
                    break

            # If we get here, either output is None or refusal was detected
            if attempt < self.retries:
                if output is None:
                    logger.warning(
                        f"No OUTPUT found (attempt {attempt + 1}/{self.retries + 1}), retrying with prefill"
                    )
                else:
                    logger.warning(
                        f"Refusal detected (attempt {attempt + 1}/{self.retries + 1}), retrying with prefill"
                    )
                continue
            else:
                logger.error(
                    f"Failed to generate valid output after {self.retries + 1} attempts"
                )
                raise ValueError(
                    f"Failed to generate valid output after {self.retries + 1} attempts. "
                    f"Last output: {output[:100] if output else 'None'}, "
                    f"XML length: {len(xml) if xml else 0}"
                )

        # Extract scratchpad and output from final successful response
        scratchpad = XMLParser.extract_tag(xml, "SCRATCHPAD_REASONING")
        output = XMLParser.extract_tag(xml, "OUTPUT")

        if self.transforms:
            original_output = output
            output = self.transforms(output)
            logger.debug(f"Transforms applied: {original_output} -> {output}")

        logger.debug(f"Response generated: {output}")
        return xml, scratchpad, output

    async def _call_llm(self, prefill: str | None = None) -> str:
        """Call LLM with system prompt and conversation history."""
        messages = self.conversation.copy()
        if prefill:
            messages.append({"role": "assistant", "content": prefill})

        logger.debug(
            f"Calling LLM (model={self.model.value}, messages={len(messages)}, prefill={'Yes' if prefill else 'No'})"
        )
        try:
            if self.model == RedTeamModel.CLAUDE_SONNET_4_5:
                # Anthropic API
                message = await self.client.messages.create(
                    model=self.model.value,
                    max_tokens=4096,
                    system=self.system_prompt,
                    messages=messages,
                )
                logger.debug(
                    f"LLM response received (tokens: {message.usage.output_tokens})"
                )
                return message.content[0].text
            else:
                # OpenAI API
                openai_messages = [
                    {"role": "system", "content": self.system_prompt}
                ] + messages
                response = await self.client.chat.completions.create(
                    model=self.model.value,
                    max_completion_tokens=4096,
                    messages=openai_messages,
                )
                logger.debug(
                    f"LLM response received (tokens: {response.usage.completion_tokens})"
                )
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise
