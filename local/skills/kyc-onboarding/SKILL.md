---
name: kyc-onboarding
description: Know-Your-Customer checklist to onboard a new natural-person customer at RufusBank (documents, risk level, next steps). Use when a user wants to open an account or asks what documents are required.
---

# KYC Onboarding (Persona Natural)

## Steps
1. Ask for: full name, ID type (CC, CE, Pasaporte), ID number, date of birth, occupation, monthly income.
2. Classify risk:
   - LOW: employee / pensioner, income < 20M COP.
   - MEDIUM: independent worker OR income >= 20M COP.
   - HIGH: PEP (politically exposed person) or foreign-currency operations > 10k USD/month.
3. Required documents by risk:
   - LOW: ID copy.
   - MEDIUM: ID copy + last 3 bank statements.
   - HIGH: ID copy + bank statements + source-of-funds declaration + compliance-officer approval.
4. Always end with: "Recuerda: RufusBank nunca te pedirá claves por teléfono o chat."

## Output format
Return a short table: Field | Value, then the risk level in bold, then the documents checklist.
