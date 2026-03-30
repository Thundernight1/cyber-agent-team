import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    pass

    print("SUCCESS: Imported AgentTask")
except ImportError as e:
    print(f"FAILURE: {e}")
    import core.base_agent

    print(f"core.base_agent has attributes: {dir(core.base_agent)}")
