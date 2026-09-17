from dataclasses import dataclass


@dataclass
class BranchDataclass:
    company_name: str | None = None
    branch_name: str | None = None
    branch_operator: str | None = None
    branch_address: str | None = None
    phone_number: str | None = None
    email_address: str | None = None
    company_id: str | None = None
    tax_id: str | None = None
    establishment_id: str | None = None
    facility_id: str | None = None
    opening_hours: str | None = None
