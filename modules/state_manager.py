import json
import os

class StateManager:
    def __init__(self, state_file="recovery.json"):
        self.state_file = os.path.join(os.path.dirname(__file__), '..', state_file)

    def save_state(self, queue, current_index, current_stage="idle"):
        """Save the current active job state."""
        state = {
            "queue": queue,
            "current_index": current_index,
            "current_stage": current_stage,
            "active": True
        }
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=4)
        except Exception:
            pass

    def load_state(self):
        """Load the recovery state."""
        if not os.path.exists(self.state_file):
            return None
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except:
            return None

    def clear_state(self):
        """Clear state on clean exit."""
        if os.path.exists(self.state_file):
            try:
                os.remove(self.state_file)
            except:
                pass
