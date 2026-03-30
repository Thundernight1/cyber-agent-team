import asyncio
import importlib
import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from core.base_agent import BaseAgent  # noqa: E402


async def verify_operator(module_name: str, class_name: str) -> bool:
    print(f"--- Verifying {class_name} from {module_name} ---")
    try:
        module = importlib.import_module(module_name)
        operator_class = getattr(module, class_name)

        # Check inheritance
        if not issubclass(operator_class, BaseAgent):
            print(f"FAILED: {class_name} does not inherit from BaseAgent")
            return False

        # Instantiate
        operator = operator_class(name=f"Test_{class_name}")

        # Check for execute_task
        if not hasattr(operator, "execute_task"):
            print(f"FAILED: {class_name} does not have execute_task method")
            return False

        # Check for validate_input
        if not hasattr(operator, "validate_input"):
            print(f"FAILED: {class_name} does not have validate_input method")
            return False

        # Dry run execute_task with dummy data
        print(f"Running dry-run for {class_name}...")
        result = await operator.execute_task(
            "{'action': 'verify', 'target': '127.0.0.1'}"
        )
        status = result.status if hasattr(result, "status") else "No status"
        print(f"Dry-run result: {status}")

        print(f"SUCCESS: {class_name} verified.")
        return True
    except Exception as e:
        print(f"FAILED: Exception during verification of {class_name}: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    operators = [
        ("agents.operator.network_operator", "NetworkOperator"),
        ("agents.operator.passive_operator", "PassiveOperator"),
        ("agents.operator.wireless_operator", "WirelessOperator"),
    ]

    results = []
    for module_name, class_name in operators:
        results.append(await verify_operator(module_name, class_name))

    if all(results):
        print("\nALL OPERATORS VERIFIED SUCCESSFULLY.")
        sys.exit(0)
    else:
        print("\nSOME OPERATORS FAILED VERIFICATION.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
