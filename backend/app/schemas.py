from pydantic import BaseModel, Field


class Transaction(BaseModel):
    amount_usd: float = Field(ge=0)
    hours_since_last_txn: float = Field(ge=0)
    txn_count_last_24h: int = Field(ge=0)
    distance_from_home_km: float = Field(ge=0)
    card_age_months: int = Field(ge=0)
    customer_age: int = Field(ge=0, le=120)
    account_balance_usd: float
    cvv_retry_count: int = Field(ge=0)
    velocity_score: float
    time_of_day_hour: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6)
    merchant_risk_score: float
    prior_disputes: int = Field(ge=0)
    merchant_category: str
    card_type: str
    auth_method: str
    channel: str
    device_type: str
    is_foreign_transaction: bool
    is_new_merchant: bool
    used_vpn: bool
    ip_country_mismatch: bool
    billing_shipping_mismatch: bool
    is_ai_generated_scam_attempt: bool


class Reason(BaseModel):
    feature: str
    value: str | float | bool
    impact: float          # log-odds contribution; positive pushes toward fraud


class Prediction(BaseModel):
    fraud_probability: float
    flagged: bool
    threshold: float
    top_reasons: list[Reason]


class BatchRequest(BaseModel):
    transactions: list[Transaction] = Field(min_length=1, max_length=1000)


class BatchResponse(BaseModel):
    predictions: list[Prediction]