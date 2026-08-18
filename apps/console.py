"""
SAGE Situated Companion
Roadmap 2 — Console Application

Provides the first runnable human-facing application built around
the verified SAGE Core V1 architecture.

The console composes the external interface adapters with SageRuntime
without placing application-specific behavior inside the frozen core.
"""

from interfaces.basic_generation import BasicGenerationAdapter
from interfaces.basic_input import BasicInputAdapter
from interfaces.basic_output import BasicOutputAdapter
from interfaces.contracts import ExternalInput, OutputRequest

from sage.intervention import InterventionAction
from sage.runtime import SageRuntime


class SageConsole:
    """
    Runnable console application for SAGE.

    The console accepts human text, translates it into normalized
    external input, passes it through the SAGE runtime, generates
    approved content, and delivers the resulting output.
    """

    def __init__(
        self,
        *,
        runtime: SageRuntime | None = None,
        preferred_address: str | None = None,
    ):
        self.runtime = runtime or SageRuntime()
        self.preferred_address = preferred_address

        self.input_adapter = BasicInputAdapter()
        self.generation_adapter = BasicGenerationAdapter()
        self.output_adapter = BasicOutputAdapter()

    def process_message(
        self,
        message: str,
    ) -> str | None:
        """
        Process one human message through the complete SAGE pipeline.

        Returns generated output when the intervention engine approves
        a response. Returns None when SAGE elects not to speak.
        """

        message = message.strip()

        if not message:
            return None

        external_input = ExternalInput(
            source="console_user",
            input_type="request",
            payload={
                "text": message,
            },
            confidence=1.0,
        )

        event = self.input_adapter.to_situated_event(
            external_input
        )

        # Retrieve relevant memories BEFORE processing event
        # This way, memories are from previous interactions,
        # not from the current event being processed
        relevant_memories = (
            self.runtime.memory.retrieve_relevant_memories(
                query=message,
                limit=3,
                min_importance=0.4,
            )
        )

        runtime_result = self.runtime.ingest_event(
            event
        )

        decision = runtime_result["decision"]

        if decision.action not in {
            InterventionAction.RESPOND,
            InterventionAction.INTERRUPT,
        }:
            return None

        context_snapshot = runtime_result["context"]

        communication_mode = (
            runtime_result["communication_mode"].value
        )

        generated_content = (
            self.generation_adapter.generate(
                instruction=message,
                context={
                    "location": context_snapshot.location,
                    "activity": context_snapshot.activity,
                    "conversation_topic": (
                        context_snapshot.conversation_topic
                    ),
                    "safety_level": (
                        context_snapshot.safety_level
                    ),
                },
                personality={
                    "preferred_address": (
                        self.preferred_address
                    ),
                },
                communication_mode=communication_mode,
                memories=relevant_memories,
            )
        )

        output_request = OutputRequest(
            content=generated_content,
            output_type="text",
            priority=decision.priority,
            metadata={
                "source": external_input.source,
                "decision_action": decision.action.value,
                "decision_reason": decision.reason,
                "communication_mode": communication_mode,
            },
        )

        output_result = self.output_adapter.deliver(
            output_request
        )

        if not output_result.success:
            return None

        return output_result.metadata["content"]

    def run(self) -> None:
        """
        Start the interactive SAGE console.
        """

        self.runtime.start()

        print("SAGE Situated Companion")
        print("Console runtime active.")
        print("Type 'exit' or 'quit' to stop.")
        print()

        try:
            while True:
                message = input("You: ").strip()

                if message.lower() in {
                    "exit",
                    "quit",
                }:
                    break

                response = self.process_message(
                    message
                )

                if response is not None:
                    print(f"Sage: {response}")

        except (EOFError, KeyboardInterrupt):
            print()

        finally:
            self.runtime.stop()
            print("SAGE console stopped.")


def main() -> None:
    """
    Launch the SAGE console application.
    """

    console = SageConsole(
        preferred_address="Queen"
    )

    console.run()


if __name__ == "__main__":
    main()
