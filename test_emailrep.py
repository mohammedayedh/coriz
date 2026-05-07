import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'external_tools', 'Coriza-Tool-Pro', 'emailprocheck'))
import emailprocheck

print("Testing emailrep.io...")
result = emailprocheck.run_emailrep("test@gmail.com")
print(f"Result: {result}")
