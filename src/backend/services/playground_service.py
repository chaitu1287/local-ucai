"""Service for playground execution."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from jinja2 import Template
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
import src.database.models as db
from src.backend.services.eval_service import EvalService


class PlaygroundService:
    """Handles playground creation and management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.eval_service = EvalService(session)

    def _to_domain_objects(
        self,
        l3_risk: db.L3Risk,
        l3_attack: db.L3Attack,
        context: db.Context,
        rubric: Optional[db.Rubric] = None,
    ) -> dict[str, Any]:
        """Construct template-friendly dictionaries for rendering."""
        rubric_dict = {
            "name": rubric.name if rubric else "",
            "description": rubric.description if rubric else "",
            "content": rubric.content if rubric else "",
        }

        l1_risk = l3_risk.l2_risk.l1_risk
        risk_dict = {
            "l1": {
                "name": l1_risk.name,
                "description": l1_risk.description,
            },
            "l2": {
                "name": l3_risk.l2_risk.name,
                "description": l3_risk.l2_risk.description,
            },
            "l3": {
                "name": l3_risk.name,
                "description": l3_risk.description,
            },
            "description": l3_risk.description,
            "rubric": rubric_dict,
        }

        l1_attack = l3_attack.l2_attack.l1_attack
        attack_dict = {
            "l1": {
                "name": l1_attack.name,
                "description": getattr(l1_attack, "description", ""),
            },
            "l2": {
                "name": l3_attack.l2_attack.name,
                "description": l3_attack.l2_attack.description,
            },
            "l3": {
                "name": l3_attack.name,
                "description": l3_attack.description,
            },
            "description": l3_attack.description,
            "transforms": [],
        }

        product_db = context.product
        platform_value = (
            product_db.platform.value
            if hasattr(product_db.platform, "value")
            else product_db.platform
        )

        product_dict = {
            "name": product_db.name,
            "type": product_db.type,
            "platform": platform_value,
            "description": product_db.description,
            "use_cases": product_db.use_cases.get("use_cases", []),
        }

        context_dict = {
            "name": context.name,
            "description": context.description,
            "industry": context.industry,
            "environment": context.environment,
            "product": product_dict,
        }

        return {
            "risk": risk_dict,
            "attack": attack_dict,
            "context": context_dict,
            "product": product_dict,
            "rubric": rubric_dict,
        }

    async def generate_prompt(
        self,
        l3_risk_id: UUID,
        l3_attack_id: UUID,
        context_id: UUID,
        prompt_template_id: Optional[UUID] = None,
        template_content: Optional[str] = None,
        agent_config_id: Optional[UUID] = None,
        rubric_id: Optional[UUID] = None,
        turns: int = 1,
    ) -> tuple[str, dict[str, Any]]:
        """Generate a prompt by rendering the template with context variables."""
        if not prompt_template_id and not template_content:
            raise ValueError(
                "Either prompt_template_id or template_content must be provided"
            )

        # Fetch L3 Risk with hierarchy
        result = await self.session.execute(
            select(db.L3Risk)
            .options(joinedload(db.L3Risk.l2_risk).joinedload(db.L2Risk.l1_risk))
            .filter(db.L3Risk.id == l3_risk_id)
        )
        l3_risk = result.unique().scalar_one_or_none()
        if not l3_risk:
            raise ValueError(f"L3 Risk {l3_risk_id} not found")

        # Fetch L3 Attack with hierarchy
        result = await self.session.execute(
            select(db.L3Attack)
            .options(
                joinedload(db.L3Attack.l2_attack).joinedload(db.L2Attack.l1_attack)
            )
            .filter(db.L3Attack.id == l3_attack_id)
        )
        l3_attack = result.unique().scalar_one_or_none()
        if not l3_attack:
            raise ValueError(f"L3 Attack {l3_attack_id} not found")

        # Fetch Context with product
        result = await self.session.execute(
            select(db.Context)
            .options(joinedload(db.Context.product))
            .filter(db.Context.id == context_id)
        )
        context = result.unique().scalar_one_or_none()
        if not context:
            raise ValueError(f"Context {context_id} not found")

        # Get Template Content
        template_str = template_content
        if not template_str and prompt_template_id:
            result = await self.session.execute(
                select(db.PromptTemplate).filter(
                    db.PromptTemplate.id == prompt_template_id,
                    ~db.PromptTemplate.is_deleted,
                )
            )
            template = result.scalar_one_or_none()
            if not template:
                raise ValueError(f"Prompt Template {prompt_template_id} not found")
            template_str = template.template

        if not template_str:
            raise ValueError("No template content available")

        # Fetch Rubric if provided
        rubric = None
        if rubric_id:
            result = await self.session.execute(
                select(db.Rubric).filter(
                    db.Rubric.id == rubric_id, ~db.Rubric.is_deleted
                )
            )
            rubric = result.scalar_one_or_none()

        template_variables = self._to_domain_objects(
            l3_risk, l3_attack, context, rubric
        )

        render_context = {
            **template_variables,
            "turns": turns,
        }

        try:
            jinja_template = Template(template_str)
            rendered_prompt = jinja_template.render(**render_context)
        except Exception as e:
            raise ValueError(f"Failed to render template: {str(e)}")

        return rendered_prompt, template_variables

    async def create_playground_execution(
        self,
        l3_risk_id: UUID,
        l3_attack_id: UUID,
        agent_config_id: UUID,
        context_id: UUID,
        prompt_template_id: Optional[UUID] = None,
        template_content: Optional[str] = None,
        rubric_id: Optional[UUID] = None,
        turns: int = 3,
        prompt_text: Optional[str] = None,
        username: Optional[str] = None,
    ) -> db.Eval:
        """Create a playground batch with single eval."""
        if not prompt_template_id and not template_content:
            raise ValueError(
                "Either prompt_template_id or template_content must be provided"
            )

        result = await self.session.execute(
            select(db.L3Risk).filter(db.L3Risk.id == l3_risk_id, ~db.L3Risk.is_deleted)
        )
        risk = result.scalar_one_or_none()
        if not risk:
            raise ValueError(f"L3 Risk {l3_risk_id} not found")

        result = await self.session.execute(
            select(db.L3Attack).filter(
                db.L3Attack.id == l3_attack_id, ~db.L3Attack.is_deleted
            )
        )
        attack = result.scalar_one_or_none()
        if not attack:
            raise ValueError(f"L3 Attack {l3_attack_id} not found")

        result = await self.session.execute(
            select(db.AgentConfig).filter(
                db.AgentConfig.id == agent_config_id, ~db.AgentConfig.is_deleted
            )
        )
        if not result.scalar_one_or_none():
            raise ValueError(f"Agent Config {agent_config_id} not found")

        result = await self.session.execute(
            select(db.Context).filter(
                db.Context.id == context_id, ~db.Context.is_deleted
            )
        )
        if not result.scalar_one_or_none():
            raise ValueError(f"Context {context_id} not found")

        # Handle Template
        template_id = prompt_template_id
        if template_content:
            timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
            temp_name = (
                f"{username} - {timestamp}"
                if username
                else f"Playground Template - {timestamp}"
            )
            new_template = db.PromptTemplate(
                name=temp_name,
                version=1,
                template=template_content,
                preview=True,
            )
            self.session.add(new_template)
            await self.session.flush()
            template_id = new_template.id
        elif prompt_template_id:
            result = await self.session.execute(
                select(db.PromptTemplate).filter(
                    db.PromptTemplate.id == prompt_template_id,
                    ~db.PromptTemplate.is_deleted,
                )
            )
            if not result.scalar_one_or_none():
                raise ValueError(f"Prompt Template {prompt_template_id} not found")

        if not template_id:
            raise ValueError("Failed to resolve prompt template")

        # Check Rubric if provided, otherwise fall back to default playground rubric
        playground_rubric_id = rubric_id
        if rubric_id:
            result = await self.session.execute(
                select(db.Rubric).filter(
                    db.Rubric.id == rubric_id, ~db.Rubric.is_deleted
                )
            )
            if not result.scalar_one_or_none():
                raise ValueError(f"Rubric {rubric_id} not found")
        else:
            result = await self.session.execute(
                select(db.Rubric).filter(
                    db.Rubric.name == "Playground Default Rubric", ~db.Rubric.is_deleted
                )
            )
            default_rubric = result.scalar_one_or_none()
            if not default_rubric:
                default_rubric = db.Rubric(
                    name="Playground Default Rubric",
                    description="Default rubric for playground evaluations",
                    content="Use default grading criteria",
                )
                self.session.add(default_rubric)
                await self.session.flush()
            playground_rubric_id = default_rubric.id

        prompt_content = prompt_text
        if not prompt_content:
            prompt_content, _ = await self.generate_prompt(
                l3_risk_id=l3_risk_id,
                l3_attack_id=l3_attack_id,
                context_id=context_id,
                prompt_template_id=prompt_template_id if not template_content else None,
                template_content=template_content,
                agent_config_id=agent_config_id,
                rubric_id=playground_rubric_id,
                turns=turns,
            )

        config = db.Config(
            name=f"Playground - {risk.name} x {attack.name}",
            prompt_template_id=template_id,
            agent_config_id=agent_config_id,
            context_id=context_id,
            description="Temporary config for playground",
            turns=turns,
            preview=True,
        )
        self.session.add(config)
        await self.session.flush()

        batch = db.Batch(
            config_id=config.id,
            status=db.BatchStatus.RUNNING,
            preview=True,
        )
        self.session.add(batch)
        await self.session.flush()

        prompt = db.Prompt(template_id=template_id, value=prompt_content)
        self.session.add(prompt)
        await self.session.flush()

        conversation = db.Conversation(history=[])
        self.session.add(conversation)
        await self.session.flush()

        eval_obj = db.Eval(
            batch_id=batch.id,
            prompt_id=prompt.id,
            conversation_id=conversation.id,
            rubric_id=playground_rubric_id,
            l3_risk_id=l3_risk_id,
            l3_attack_id=l3_attack_id,
            status=db.EvalStatus.PENDING,
            preview=True,
        )
        self.session.add(eval_obj)
        await self.session.flush()

        return eval_obj
