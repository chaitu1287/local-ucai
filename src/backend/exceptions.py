"""Custom exceptions for backend operations."""


class EvalNotFoundException(Exception):
    """Raised when an eval is not found."""

    def __init__(self, eval_id):
        self.eval_id = eval_id
        super().__init__(f"Eval {eval_id} not found")
