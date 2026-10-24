"""Run the existing Sage pipeline with explicitly approved public test text."""

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from apps.console import SageConsole
from apps.companion_session import CompanionSession
from interfaces.huggingface_generation import HuggingFaceGenerationAdapter
from sage.memory import MemoryStore
from sage.runtime import SageRuntime


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-cloud-text", action="store_true",
                        help="Approve sending entered public test text to the Sage HF Space")
    args = parser.parse_args()
    if not args.allow_cloud_text:
        parser.error("Cloud text is off. Read docs/HUGGINGFACE_COMPANION_TEST.md first.")
    with TemporaryDirectory(prefix="sage-test-") as folder:
        runtime = SageRuntime()
        # Isolate this test session from the user's durable memory file.
        runtime.memory = MemoryStore(str(Path(folder) / "memory.json"))
        console = SageConsole(runtime=runtime, preferred_address="Queen",
                              generation_adapter=HuggingFaceGenerationAdapter())
        session = CompanionSession(console)
        session.start(allow_cloud_text=True)
        print("Sage public-text test. Camera/microphone/location OFF. Type /stop to end.")
        try:
            while True:
                text = input("You: ").strip()
                if text == "/stop":
                    break
                if not text:
                    continue
                try:
                    answer = session.respond(text)
                    if answer is not None:
                        print(f"Sage: {answer}")
                except Exception:
                    # Avoid logging service errors that could contain prompt data.
                    print("Sage could not answer. Check service availability; no automatic retry.")
        except (EOFError, KeyboardInterrupt):
            pass
        finally:
            session.stop()


if __name__ == "__main__":
    main()
