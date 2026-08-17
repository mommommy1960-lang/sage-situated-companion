"""
SAGE Situated Companion
Roadmap 2 — Basic Output Adapter

Provides the first concrete implementation of the OutputAdapter
contract.

This deterministic adapter simulates successful delivery of SAGE
output while remaining independent from any specific display,
speaker, device, operating system, or hardware platform.
"""

from interfaces.contracts import (
    OutputAdapter,
    OutputRequest,
    OutputResult,
)


class BasicOutputAdapter(OutputAdapter):
    """
    Generic concrete output adapter.

    This implementation records a normalized successful delivery
    result without depending on any external hardware or service.
    """

    def deliver(
        self,
        request: OutputRequest,
    ) -> OutputResult:
        """
        Deliver an OutputRequest through the basic adapter.
        """

        if not request.content.strip():
            return OutputResult(
                success=False,
                adapter="basic_output",
                output_type=request.output_type,
                error="empty_content",
            )

        return OutputResult(
            success=True,
            adapter="basic_output",
            output_type=request.output_type,
            metadata={
                "content": request.content,
                "priority": request.priority,
                "request_metadata": request.metadata,
            },
        )
