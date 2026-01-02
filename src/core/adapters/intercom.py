import asyncio
import logging
import os
from uuid import uuid4

from httpx import AsyncClient

from src.core.adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class IntercomAdapter(BaseAdapter):
    """Adapter for Intercom customer platform."""

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("INTERCOM_API_KEY")
        if not self.api_key:
            raise ValueError("INTERCOM_API_KEY environment variable is required")

        self.base_url = "https://api.intercom.io"
        self.contact_id = None
        self.conversation_id = None
        self.last_part_index = -1

    async def setup(self) -> None:
        """Initialize Intercom connection and create a unique contact."""
        logger.info("Setting up Intercom adapter")
        self.client = AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Intercom-Version": "2.14",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

        email = f"{uuid4()}@eval.aiuc.com"
        logger.debug(f"Creating contact with email: {email}")
        contact_response = await self.client.post(
            "/contacts",
            json={
                "role": "user",
                "external_id": str(uuid4()),
                "email": email,
                "name": "Test User",
            },
        )
        contact_response.raise_for_status()
        contact_data = contact_response.json()
        self.contact_id = contact_data["id"]
        logger.info(f"Intercom contact created: {self.contact_id}")

    async def interact(self, message: str) -> str:
        """Send message to Intercom conversation and return agent response."""
        logger.debug(f"Sending message to Intercom: {message}")

        if self.conversation_id is None:
            # First turn: Create conversation
            logger.debug("Creating new conversation")
            create_response = await self.client.post(
                "/conversations",
                json={
                    "from": {
                        "type": "user",
                        "id": self.contact_id,
                    },
                    "body": message,
                },
            )
            create_response.raise_for_status()
            conversation_data = create_response.json()
            # Extract conversation_id, not id (id is the message ID)
            self.conversation_id = conversation_data.get("conversation_id")
            logger.info(f"Conversation created: {self.conversation_id}")
        else:
            # Subsequent turns: Reply to conversation
            logger.debug(f"Replying to conversation {self.conversation_id}")
            try:
                reply_response = await self.client.post(
                    f"/conversations/{self.conversation_id}/reply",
                    json={
                        "message_type": "comment",
                        "type": "user",
                        "intercom_user_id": self.contact_id,
                        "body": message,
                    },
                )
                reply_response.raise_for_status()
            except Exception as e:
                # Log the error details for debugging
                logger.error(f"Failed to reply to conversation {self.conversation_id}")
                logger.error(f"Contact ID: {self.contact_id}")
                logger.error(f"Message: {message[:100]}")
                if hasattr(e, "response"):
                    logger.error(f"Response status: {e.response.status_code}")
                    logger.error(f"Response body: {e.response.text}")
                raise

        # Wait for and poll for agent response
        conversation, responses = await self._wait_for_response()
        return responses

    async def _wait_for_response(
        self, max_wait_seconds: int = 10, poll_interval: float = 1.0
    ) -> tuple[dict, str]:
        """Poll the conversation for the full duration to collect all agent responses."""
        start_time = asyncio.get_event_loop().time()
        responses = []
        conversation = None
        first_response_time = None

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time

            # Poll
            if elapsed > max_wait_seconds:
                if not responses:
                    logger.warning(f"No response received after {max_wait_seconds}s")
                else:
                    logger.info(
                        f"Collected {len(responses)} response part(s) over {max_wait_seconds}s"
                    )

                # Final poll to get latest conversation state
                if conversation is None:
                    retrieve_response = await self.client.get(
                        f"/conversations/{self.conversation_id}"
                    )
                    retrieve_response.raise_for_status()
                    conversation = retrieve_response.json()

                return conversation, "\n".join(responses) if responses else ""

            # Poll conversation
            logger.debug(f"Polling attempt (elapsed: {elapsed:.1f}s)")
            retrieve_response = await self.client.get(
                f"/conversations/{self.conversation_id}"
            )
            retrieve_response.raise_for_status()
            conversation = retrieve_response.json()

            # Extract new responses
            response_text = self._extract_latest(conversation)

            if response_text:
                if first_response_time is None:
                    first_response_time = elapsed
                    logger.debug(
                        f"First response received at {elapsed:.1f}s: {response_text[:100]}..."
                    )
                else:
                    logger.debug(
                        f"Additional response at {elapsed:.1f}s: {response_text[:100]}..."
                    )

                responses.append(response_text)

            # Wait before next poll
            await asyncio.sleep(poll_interval)

    def _extract_latest(self, conversation: dict) -> str:
        """Extract latest admin/bot responses from conversation data."""
        responses = []
        conversation_parts_data = conversation.get("conversation_parts", {})
        parts = conversation_parts_data.get("conversation_parts", [])

        for idx, part in enumerate(parts):
            # Only process new parts
            if idx <= self.last_part_index:
                continue

            # Filter for admin/bot comment responses
            part_type = part.get("part_type")
            author = part.get("author", {})
            author_type = author.get("type")

            if part_type == "comment" and author_type in ["admin", "bot"]:
                body = part.get("body", "")
                if body:
                    responses.append(body)

        # Update tracking to current highest index
        if parts:
            self.last_part_index = len(parts) - 1

        # Concatenate all new admin responses
        final_response = "\n".join(responses) if responses else ""
        return final_response

    async def close(self) -> None:
        """Close the Intercom conversation and clean up resources."""
        logger.info("Closing Intercom adapter")
        if self.client:
            await self.client.aclose()
