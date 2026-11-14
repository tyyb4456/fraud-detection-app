type Field = [key: string, label: string];

export const NUMERIC: Field[] = [
  ["amount_usd", "Amount (USD)"],
  ["hours_since_last_txn", "Hours since last txn"],
  ["txn_count_last_24h", "Txns in last 24h"],
  ["distance_from_home_km", "Distance from home (km)"],
  ["card_age_months", "Card age (months)"],
  ["customer_age", "Customer age"],
  ["account_balance_usd", "Account balance (USD)"],
  ["cvv_retry_count", "CVV retries"],
  ["velocity_score", "Velocity score"],
  ["time_of_day_hour", "Hour of day (0-23)"],
  ["day_of_week", "Day of week (0-6)"],
  ["merchant_risk_score", "Merchant risk score"],
  ["prior_disputes", "Prior disputes"],
];

export const CATS: Field[] = [
  ["merchant_category", "Merchant category"],
  ["card_type", "Card type"],
  ["auth_method", "Auth method"],
  ["channel", "Channel"],
  ["device_type", "Device type"],
];

export const BOOLS: Field[] = [
  ["is_foreign_transaction", "Foreign transaction"],
  ["is_new_merchant", "New merchant"],
  ["used_vpn", "Used VPN"],
  ["ip_country_mismatch", "IP country mismatch"],
  ["billing_shipping_mismatch", "Billing/shipping mismatch"],
  ["is_ai_generated_scam_attempt", "AI-generated scam attempt"],
];

export const pretty = (s: string) => s.replaceAll("_", " ");