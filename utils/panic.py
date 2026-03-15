import os
import shutil
from utils.logger import Logger

def trigger_panic():
    """
    Emergency function to wipe sensitive configuration and logs.
    """
    Logger.critical("PANIC BUTTON TRIGGERED!")

    files_to_delete = [
        ".env",
        "logs/aura.log",
        "data/db/aura.db"
    ]

    for f in files_to_delete:
        if os.path.exists(f):
            try:
                os.remove(f)
                Logger.warning(f"Deleted: {f}")
            except Exception as e:
                Logger.error(f"Failed to delete {f}: {e}")

    Logger.info("Shredding session data...")
    # In a real scenario, we might use 'srm' or overwrite bytes

    Logger.success("Cleanup complete. Exiting.")
    exit(0)
