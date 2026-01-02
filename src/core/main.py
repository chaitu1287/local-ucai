import asyncio
import argparse
from datetime import datetime
import logging

from src.core.batch.runner import Runner
from src.core.utils.logging import setup_logging, log_section

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AIUC adversarial evaluations")
    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML config file",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level",
    )

    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/eval_{timestamp}.log"
    setup_logging(log_level=args.log_level, log_file=log_file)

    async def run():
        logger.info(f"Starting evaluation from config: {args.config}")
        runner = Runner(args.config)

        try:
            # Check if preview mode
            if runner.config.get("preview", False):
                logger.info("Preview mode enabled in config")
                results = await runner.preview()
                summary = "Preview complete!\n"
                summary += f"Eval ID: {runner.eval_id}\n"
                summary += f"Generated {len(results)} first messages\n"
                summary += (
                    f"Preview saved to: preview/{runner.eval_id}/first_messages.json\n"
                )
            else:
                results = await runner.run()
                summary = "Evaluation complete!\n"
                summary += f"Eval ID: {runner.eval_id}\n"
                summary += "Categories processed:\n"
                for category, runs in results.items():
                    summary += f"  - {category}: {len(runs)} runs\n"

            log_section(logger, "INFO", "COMPLETE", summary)

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            raise

    asyncio.run(run())
