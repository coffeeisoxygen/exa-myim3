# Application name
APP_NAME = "EXA-MYIM3"

# Key codes
KEY_CODES = {
    "HOME": 3,
    "BACK": 4,
    "MENU": 82,
}

TRANSACTION_STATUS = {
    0: "Not Processed",
    1: "In Progress",
    2: "Success",
    3: "Failed",
    4: "Manual Intervention",
}

# Automation Task Status
AUTOMATION_STATUS = {
    0: "Not Processed",
    1: "In Progress",
    2: "Completed",
    3: "Failed",
    4: "Need Manual Intervention",
}

# Mapping Automation Status ke Transaction Status
AUTOMATION_TO_TRANSACTION = {
    0: 0,  # Not Processed -> Not Processed
    1: 1,  # In Progress -> In Progress
    2: 2,  # Completed -> Success
    3: 3,  # Failed -> Failed
    4: 4,  # Need Manual Intervention -> Manual Intervention
}


# Fungsi untuk convert otomatisasi ke transaksi
def map_automation_to_transaction(automation_status: int) -> int:
    return AUTOMATION_TO_TRANSACTION.get(
        automation_status, 0
    )  # Default ke Not Processed
