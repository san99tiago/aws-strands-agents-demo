---
name: fraud-triage
description: Triage a suspicious card transaction reported by a customer (block, dispute, or monitor). Use when the user mentions an unknown charge, fraud, stolen card or phishing.
---

# Fraud Triage

1. Ask (if missing): last 4 digits, amount, merchant, date.
2. Decide:
   - Card lost/stolen OR phishing -> BLOCK card immediately + issue replacement.
   - Unknown charge, card in possession -> open DISPUTE (chargeback) within 15 days.
   - Small recurring charge (< 50.000 COP) the user may recognize -> MONITOR + explain.
3. Never ask for the full card number, CVV or passwords.
4. Give a case number with format FR-YYYYMMDD-XXXX.
