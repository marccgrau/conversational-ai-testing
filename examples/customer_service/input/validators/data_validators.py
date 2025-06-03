from util import get_dict_json

from simulator.utils.file_reading import validator

# --- common reference data ----------------------------------------------
ISO_CURRENCIES = {"USD", "GBP", "CHF", "EUR"}
KYC_STATUSES = {"verified", "pending", "rejected"}
CUSTOMER_SEGMENTS = {"retail", "wealth", "private"}
ACCOUNT_TYPES = {"checking", "savings", "current", "private_account"}
ACCOUNT_STATUSES = {"active", "dormant", "closed"}
CARD_TYPES = {"debit", "credit"}
CARD_BRANDS = {"Visa", "Mastercard", "Amex"}
CARD_STATUSES = {"active", "locked", "blocked", "expired"}
LOAN_TYPES = {"auto", "mortgage", "student", "personal"}
LOAN_STATUSES = {"active", "closed", "defaulted"}
TICKET_STATUSES = {"open", "in_progress", "resolved", "closed"}


# ---------------- customers ----------------------------------------------
@validator(table="customers")
def customers_validator(new_df, dataset):
    # string-ify any accidental dicts for safety
    for col in ["phone", "email"]:
        if col in new_df and new_df[col].dtype == "object":
            new_df[col] = new_df[col].astype(str)

    # uniqueness
    if "customers" in dataset:
        taken = set(dataset["customers"]["customer_id"])
        dupes = new_df["customer_id"].isin(taken)
        if dupes.any():
            raise ValueError(
                f"Customer IDs already exist: {new_df.loc[dupes, 'customer_id'].tolist()}"
            )

    # simple field checks
    for idx, row in new_df.iterrows():
        if row["kyc_status"] not in KYC_STATUSES:
            raise ValueError(f"Invalid kyc_status '{row['kyc_status']}'")
        if row["segment"] not in CUSTOMER_SEGMENTS:
            raise ValueError(f"Invalid segment '{row['segment']}'")
    return new_df, dataset


# ---------------- accounts -----------------------------------------------
@validator(table="accounts")
def accounts_validator(new_df, dataset):
    # account IDs unique
    if "accounts" in dataset:
        existing = set(dataset["accounts"]["account_id"])
        if new_df["account_id"].isin(existing).any():
            raise ValueError("Duplicate account_id detected")

    # fk to customers + field quality
    if "customers" in dataset:
        cust_ids = set(dataset["customers"]["customer_id"])
        for idx, row in new_df.iterrows():
            if row["customer_id"] not in cust_ids:
                raise ValueError(f"customer_id {row['customer_id']} not found")
            if row["account_type"] not in ACCOUNT_TYPES:
                raise ValueError(f"Invalid account_type '{row['account_type']}'")
            if row["status"] not in ACCOUNT_STATUSES:
                raise ValueError(f"Invalid account status '{row['status']}'")
            if row["currency"] not in ISO_CURRENCIES:
                raise ValueError(f"Unsupported currency '{row['currency']}'")
    return new_df, dataset


# ---------------- transactions -------------------------------------------
@validator(table="transactions")
def transactions_validator(new_df, dataset):
    # unique IDs
    if "transactions" in dataset:
        used = set(dataset["transactions"]["transaction_id"])
        if new_df["transaction_id"].isin(used).any():
            raise ValueError("transaction_id already exists")

    # fk & currency match
    if "accounts" in dataset:
        accounts = get_dict_json(dataset["accounts"], "account_id")
        for idx, row in new_df.iterrows():
            acc_id = row["account_id"]
            if acc_id not in accounts:
                raise ValueError(f"account_id {acc_id} not found")
            if row["currency"] != accounts[acc_id]["currency"]:
                raise ValueError(
                    f"Currency mismatch for txn {row['transaction_id']}: "
                    f"{row['currency']} vs account {accounts[acc_id]['currency']}"
                )
    return new_df, dataset


# ---------------- cards ---------------------------------------------------
@validator(table="cards")
def cards_validator(new_df, dataset):
    if "cards" in dataset:
        existing = set(dataset["cards"]["card_id"])
        if new_df["card_id"].isin(existing).any():
            raise ValueError("Duplicate card_id")

    # FKs
    custs = (
        set(dataset["customers"]["customer_id"]) if "customers" in dataset else set()
    )
    accs = set(dataset["accounts"]["account_id"]) if "accounts" in dataset else set()

    for _, row in new_df.iterrows():
        if row["customer_id"] and row["customer_id"] not in custs:
            raise ValueError(f"Unknown customer_id {row['customer_id']}")
        if row["account_id"] and row["account_id"] not in accs:
            raise ValueError(f"Unknown account_id {row['account_id']}")
        if row["card_type"] not in CARD_TYPES:
            raise ValueError(f"Invalid card_type {row['card_type']}")
        if row["brand"] not in CARD_BRANDS:
            raise ValueError(f"Invalid card brand {row['brand']}")
        if row["status"] not in CARD_STATUSES:
            raise ValueError(f"Invalid card status {row['status']}")
    return new_df, dataset


# ---------------- loans ---------------------------------------------------
@validator(table="loans")
def loans_validator(new_df, dataset):
    if "loans" in dataset:
        taken = set(dataset["loans"]["loan_id"])
        if new_df["loan_id"].isin(taken).any():
            raise ValueError("loan_id already exists")

    cust_ids = (
        set(dataset["customers"]["customer_id"]) if "customers" in dataset else set()
    )

    for _, row in new_df.iterrows():
        if row["customer_id"] not in cust_ids:
            raise ValueError(f"Unknown customer_id {row['customer_id']}")
        if row["loan_type"] not in LOAN_TYPES:
            raise ValueError(f"Invalid loan_type {row['loan_type']}")
        if row["status"] not in LOAN_STATUSES:
            raise ValueError(f"Invalid loan status {row['status']}")
        if row["currency"] not in ISO_CURRENCIES:
            raise ValueError(f"Unsupported currency {row['currency']}")
    return new_df, dataset


# ---------------- loan_payments ------------------------------------------
@validator(table="loan_payments")
def loan_payments_validator(new_df, dataset):
    # uniqueness
    if "loan_payments" in dataset:
        used = set(dataset["loan_payments"]["payment_id"])
        if new_df["payment_id"].isin(used).any():
            raise ValueError("payment_id already exists")

    # fk + numeric checks
    loans = get_dict_json(dataset["loans"], "loan_id") if "loans" in dataset else {}
    for _, row in new_df.iterrows():
        if row["loan_id"] not in loans:
            raise ValueError(f"loan_id {row['loan_id']} not found")
        if row["amount"] <= 0:
            raise ValueError("Payment amount must be positive")
        if abs(row["principal_amount"] + row["interest_amount"] - row["amount"]) > 0.01:
            raise ValueError("principal + interest must equal total amount")
    return new_df, dataset


# ---------------- support_tickets ----------------------------------------
@validator(table="support_tickets")
def support_tickets_validator(new_df, dataset):
    if "support_tickets" in dataset:
        ids = set(dataset["support_tickets"]["ticket_id"])
        if new_df["ticket_id"].isin(ids).any():
            raise ValueError("ticket_id already exists")

    cust_ids = (
        set(dataset["customers"]["customer_id"]) if "customers" in dataset else set()
    )

    for _, row in new_df.iterrows():
        if row["customer_id"] not in cust_ids:
            raise ValueError(f"Unknown customer_id {row['customer_id']}")
        if row["status"] not in TICKET_STATUSES:
            raise ValueError(f"Invalid ticket status {row['status']}")
        if row["priority"] not in {"low", "medium", "high"}:
            raise ValueError(f"Invalid priority {row['priority']}")
    return new_df, dataset
