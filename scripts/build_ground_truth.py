"""
Build verified ground-truth reference datasets for quantitative evaluation.
Compiles verified reference transactions for bsb-001 through bsb-005 and Bank Muscat.
"""

import os
import json

GROUND_TRUTH_DIR = "data/evaluation/ground_truth"
os.makedirs(GROUND_TRUTH_DIR, exist_ok=True)


def build_all_ground_truth():
    # 1. bsb-001 (Straits Capital - Singapore)
    gt_bsb001 = {
        "statement_id": "bsb-001",
        "bank": "Straits Capital",
        "country": "SG",
        "currency": "SGD",
        "opening_balance": 15450.75,
        "closing_balance": 15271.23,
        "total_debits": 2181.67,
        "total_credits": 2002.15,
        "transactions": [
            {"date": "2025-01-01", "description": "Paynow from PAYNOW TRANSFER 8373579 TO: Corp Holdings P4583998QR", "amount": 1902.69, "direction": "credit", "balance": 17353.44},
            {"date": "2025-01-01", "description": "Paynow PAYNOW TO 9547491 TO: Guardian Health & Beauty", "amount": 70.64, "direction": "debit", "balance": 17282.80},
            {"date": "2025-01-01", "description": "Fast debit PAYNOW TRANSFER 7246426 TO: SP Group OTHER", "amount": 14.47, "direction": "debit", "balance": 17268.33},
            {"date": "2025-01-01", "description": "Paynow received PAYNOW TRANSFER 2141011 TO: Original Merchant", "amount": 69.63, "direction": "credit", "balance": 17337.96},
            {"date": "2025-01-12", "description": "Fast received PAYNOW 5979135 TO: Employer Pte Ltd P1377026QR OTHER", "amount": 29.83, "direction": "credit", "balance": 17367.79},
            {"date": "2025-01-17", "description": "Paynow qr PAYNOW 9348807 TO: Cold Storage Singapore Pte Ltd P1185585QR", "amount": 528.75, "direction": "debit", "balance": 16839.04},
            {"date": "2025-01-26", "description": "Paynow qr PAYNOW QR 9752510 TO: Lazada Group", "amount": 218.18, "direction": "debit", "balance": 16620.86},
            {"date": "2025-01-27", "description": "Paynow PAYNOW QR 1564488 TO: Grab Holdings P2765200QR", "amount": 45.89, "direction": "debit", "balance": 16574.97},
            {"date": "2025-01-28", "description": "Paynow qr PAYNOW TO 1681972 TO: Cold Storage Singapore Pte Ltd P4519868QR", "amount": 15.18, "direction": "debit", "balance": 16559.79},
            {"date": "2025-01-28", "description": "Paynow to PAYNOW TO 5967276 TO: H&M Hennes & Mauritz", "amount": 36.29, "direction": "debit", "balance": 16523.50},
            {"date": "2025-01-30", "description": "Fast debit PAYNOW TO 9521556 TO: Sheng Siong Group Ltd P4825006QR OTHER", "amount": 1230.27, "direction": "debit", "balance": 15293.23},
            {"date": "2025-01-31", "description": "Fast PAYNOW TRANSFER 6622105 TO: McDonald's Restaurants Pte Ltd P9971842QR OTHER", "amount": 22.00, "direction": "debit", "balance": 15271.23}
        ]
    }
    with open(os.path.join(GROUND_TRUTH_DIR, "bsb-001.json"), "w", encoding="utf-8") as f:
        json.dump(gt_bsb001, f, indent=2)

    # 2. bsb-002 (Liberty National - US Credit Card)
    gt_bsb002 = {
        "statement_id": "bsb-002",
        "bank": "Liberty National Bank",
        "country": "US",
        "currency": "USD",
        "opening_balance": None,
        "closing_balance": None,
        "total_debits": 7699.43,
        "total_credits": 13.84,
        "transactions": [
            {"date": "2025-09-01", "description": "UBER TRIP REF: 775648 Chevron station #0441 38.2gal premium 0.00", "amount": 531.56, "direction": "debit", "balance": None},
            {"date": "2025-09-07", "description": "WHOLE FOODS MARKET REF: 369975 Walmart Supercenter #0441 self-checkout txn 0.00", "amount": 1124.43, "direction": "debit", "balance": None},
            {"date": "2025-09-08", "description": "CHIPOTLE MEXICAN McDonald's #8841 receipt 44-2019-US 0.00", "amount": 5.32, "direction": "debit", "balance": None},
            {"date": "2025-09-10", "description": "APPLE.COM/BILL REF: 945454 Netflix US monthly standard 4K plan USD 0.00", "amount": 293.13, "direction": "debit", "balance": None},
            {"date": "2025-09-12", "description": "REWARDS REDEMPTION Chase Ultimate Rewards credit ref CUR-8841 0.00", "amount": 13.84, "direction": "credit", "balance": None},
            {"date": "2025-09-13", "description": "STARBUCKS COFFEE DoorDash order #DD-44920-NYC ETA 35min 0.00", "amount": 1520.75, "direction": "debit", "balance": None},
            {"date": "2025-09-13", "description": "WALMART SUPERCENTER Kroger store #8841 receipt 44-2019-US 0.00", "amount": 28.13, "direction": "debit", "balance": None},
            {"date": "2025-09-13", "description": "SPOTIFY USA REF.: POS-188972 Hulu No Ads monthly subscription USD 0.00", "amount": 8.52, "direction": "debit", "balance": None},
            {"date": "2025-09-17", "description": "TARGET STORE Trader Joe's receipt #TJ-44920-US store 421 0.00", "amount": 1912.64, "direction": "debit", "balance": None},
            {"date": "2025-09-21", "description": "APPLE.COM/BILL Hulu No Ads monthly subscription USD 0.00", "amount": 1095.48, "direction": "debit", "balance": None},
            {"date": "2025-09-23", "description": "NETFLIX.COM Uber trip UBR-4421-002-NYC receipt 0.00", "amount": 30.21, "direction": "debit", "balance": None},
            {"date": "2025-09-26", "description": "CLOTHING STORE Gap Factory receipt #GAP-44920-NY store 88 0.00", "amount": 42.22, "direction": "debit", "balance": None},
            {"date": "2025-09-26", "description": "SPOTIFY USA Netflix US monthly standard 4K plan USD 0.00", "amount": 5.08, "direction": "debit", "balance": None},
            {"date": "2025-09-26", "description": "WALGREENS Walgreens store #0441 script fill #WLG-8841 0.00", "amount": 1065.49, "direction": "debit", "balance": None},
            {"date": "2025-09-28", "description": "COSTCO WHOLESALE REF.: POS-402448 Kroger store #8841 receipt 44-2019-US 0.00", "amount": 36.47, "direction": "debit", "balance": None}
        ]
    }
    with open(os.path.join(GROUND_TRUTH_DIR, "bsb-002.json"), "w", encoding="utf-8") as f:
        json.dump(gt_bsb002, f, indent=2)

    # 3. bsb-003 (Continental Trust - Netherlands)
    gt_bsb003 = {
        "statement_id": "bsb-003",
        "bank": "Continental Trust",
        "country": "NL",
        "currency": "EUR",
        "opening_balance": 15320.00,
        "closing_balance": 14674.96,
        "total_debits": 6628.42,
        "total_credits": 5983.38,
        "transactions": [
            {"date": "2025-05-01", "description": "BINNENKOMENDE OVERBOEKING", "amount": 114.83, "direction": "credit", "balance": None},
            {"date": "2025-05-02", "description": "SALARISBETALING", "amount": 67.97, "direction": "credit", "balance": None},
            {"date": "2025-05-07", "description": "SEPA DEBIT", "amount": 218.55, "direction": "debit", "balance": None},
            {"date": "2025-05-07", "description": "TIKKIE BETAALD", "amount": 14.57, "direction": "debit", "balance": None},
            {"date": "2025-05-08", "description": "ATM", "amount": 337.56, "direction": "debit", "balance": None},
            {"date": "2025-05-09", "description": "SALARISBETALING", "amount": 5624.95, "direction": "credit", "balance": None},
            {"date": "2025-05-10", "description": "PREMIE SEPA INCASSO", "amount": 858.91, "direction": "debit", "balance": None},
            {"date": "2025-05-11", "description": "SALARISBETALING", "amount": 138.59, "direction": "credit", "balance": None},
            {"date": "2025-05-12", "description": "SEPA INCASSO", "amount": 6.90, "direction": "debit", "balance": None},
            {"date": "2025-05-15", "description": "TIKKIE BETAALD", "amount": 1450.77, "direction": "debit", "balance": None},
            {"date": "2025-05-15", "description": "IDEAL BETALING", "amount": 578.30, "direction": "debit", "balance": None},
            {"date": "2025-05-15", "description": "BETAALVERZOEK", "amount": 392.08, "direction": "debit", "balance": None},
            {"date": "2025-05-21", "description": "TIKKIE BETAALD", "amount": 482.22, "direction": "debit", "balance": None},
            {"date": "2025-05-22", "description": "SEPA DEBIT", "amount": 19.40, "direction": "debit", "balance": None},
            {"date": "2025-05-22", "description": "BIJSCHRIJVING", "amount": 37.04, "direction": "credit", "balance": None},
            {"date": "2025-05-24", "description": "DOORLOPENDE MACHTIGING", "amount": 890.43, "direction": "debit", "balance": None},
            {"date": "2025-05-27", "description": "ATM", "amount": 338.26, "direction": "debit", "balance": None},
            {"date": "2025-05-27", "description": "ACCEPTGIRO", "amount": 183.45, "direction": "debit", "balance": None},
            {"date": "2025-05-28", "description": "PERIODIEKE OVERBOEKING", "amount": 156.96, "direction": "debit", "balance": None},
            {"date": "2025-05-28", "description": "GELDAUTOMAAT", "amount": 592.96, "direction": "debit", "balance": None},
            {"date": "2025-05-29", "description": "IDEAL", "amount": 15.29, "direction": "debit", "balance": None},
            {"date": "2025-05-31", "description": "OVERSCHRIJVING", "amount": 91.81, "direction": "debit", "balance": None}
        ]
    }
    with open(os.path.join(GROUND_TRUTH_DIR, "bsb-003.json"), "w", encoding="utf-8") as f:
        json.dump(gt_bsb003, f, indent=2)

    # 4. bsb-004 (Silk Road Banking - Hong Kong Multi-Account)
    gt_bsb004 = {
        "statement_id": "bsb-004",
        "bank": "Silk Road Banking",
        "country": "HK",
        "currency": "HKD",
        "opening_balance": None,
        "closing_balance": None,
        "total_debits": 40729.85,
        "total_credits": 36664.82,
        "transactions": [
            {"date": "2025-09-01", "description": "Faster payment FASTER PAYMENT 8742522 TO: Deliveroo P3704085QR OTHER", "amount": 153.01, "direction": "debit", "balance": 42426.99, "account_id": "acc-hkd-current"},
            {"date": "2025-09-02", "description": "Fps payment FPS TRANSFER 4317616 TO: Watsons HK OTHER", "amount": 1932.00, "direction": "debit", "balance": 40494.99, "account_id": "acc-hkd-current"},
            {"date": "2025-09-03", "description": "Fps transfer FASTER PAYMENT 1105321 TO: Deliveroo P4161927QR OTHER", "amount": 292.69, "direction": "debit", "balance": 40202.30, "account_id": "acc-hkd-current"},
            {"date": "2025-09-05", "description": "Fps received FPS TRANSFER 4035786 TO: MPF OTHER", "amount": 298.25, "direction": "credit", "balance": 40500.55, "account_id": "acc-hkd-current"},
            {"date": "2025-09-06", "description": "Chats payment FPS PAYMENT 4665823 TO: MTR P4727275QR OTHER", "amount": 1364.41, "direction": "debit", "balance": 39136.14, "account_id": "acc-hkd-current"},
            {"date": "2025-09-07", "description": "Chats payment FPS PAYMENT 4342274 TO: Fortress OTHER", "amount": 392.44, "direction": "debit", "balance": 38743.70, "account_id": "acc-hkd-current"},
            {"date": "2025-09-12", "description": "Fps FASTER PAYMENT 5098032 TO: Deliveroo OTHER", "amount": 6510.43, "direction": "debit", "balance": 32233.27, "account_id": "acc-hkd-current"},
            {"date": "2025-09-13", "description": "Fps payment FASTER PAYMENT 4534921 TO: MTR OTHER", "amount": 4771.08, "direction": "debit", "balance": 27462.19, "account_id": "acc-hkd-current"},
            {"date": "2025-09-13", "description": "Chats payment FPS TRANSFER 7940237 TO: H&M HK OTHER", "amount": 232.85, "direction": "debit", "balance": 27229.34, "account_id": "acc-hkd-current"},
            {"date": "2025-09-14", "description": "Fps transfer FASTER PAYMENT 6757548 TO: CLP Power P6643265QR OTHER", "amount": 181.62, "direction": "debit", "balance": 27047.72, "account_id": "acc-hkd-current"},
            {"date": "2025-09-14", "description": "Chats FASTER PAYMENT 9982744 TO: Zara HK OTHER", "amount": 3554.02, "direction": "debit", "balance": 23493.70, "account_id": "acc-hkd-current"},
            {"date": "2025-09-17", "description": "Fps payment FASTER PAYMENT 7869997 TO: Deliveroo OTHER", "amount": 4728.04, "direction": "debit", "balance": 18765.66, "account_id": "acc-hkd-current"},
            {"date": "2025-09-19", "description": "Fps received FPS PAYMENT 9214246 TO: RateSetter HK OTHER", "amount": 235.54, "direction": "credit", "balance": 19001.20, "account_id": "acc-hkd-current"},
            {"date": "2025-09-19", "description": "Fps FPS PAYMENT 9247994 TO: Amazon OTHER", "amount": 263.97, "direction": "debit", "balance": 18737.23, "account_id": "acc-hkd-current"},
            {"date": "2025-09-20", "description": "Chats FASTER PAYMENT 3559781 TO: H&M HK OTHER", "amount": 373.11, "direction": "debit", "balance": 18364.12, "account_id": "acc-hkd-current"},
            {"date": "2025-09-20", "description": "Fps transfer FASTER PAYMENT 6611800 TO: PARKnSHOP OTHER", "amount": 181.04, "direction": "debit", "balance": 149818.96, "account_id": "acc-usd-savings"},
            {"date": "2025-09-20", "description": "Chats received FPS PAYMENT 1748590 TO: MPF OTHER", "amount": 303.04, "direction": "credit", "balance": 150122.00, "account_id": "acc-usd-savings"},
            {"date": "2025-09-21", "description": "Fps payment FASTER PAYMENT 4056036 TO: PARKnSHOP OTHER", "amount": 11286.99, "direction": "debit", "balance": 138835.01, "account_id": "acc-usd-savings"},
            {"date": "2025-09-22", "description": "Fps FPS TRANSFER 5047871 TO: CLP Power P1023774QR OTHER", "amount": 219.06, "direction": "debit", "balance": 138615.95, "account_id": "acc-usd-savings"},
            {"date": "2025-09-23", "description": "Faster payment received FPS 6678346 TO: Uniqlo HK OTHER", "amount": 34690.79, "direction": "credit", "balance": 173306.74, "account_id": "acc-usd-savings"},
            {"date": "2025-09-23", "description": "Fps received FPS PAYMENT 3097388 TO: RateSetter HK OTHER", "amount": 506.03, "direction": "credit", "balance": 173812.77, "account_id": "acc-usd-savings"},
            {"date": "2025-09-24", "description": "Faster payment FPS 4492099 TO: Netflix P4534921QR OTHER", "amount": 3816.32, "direction": "debit", "balance": 169996.45, "account_id": "acc-usd-savings"},
            {"date": "2025-09-27", "description": "Fps FPS 9447144 TO: Wellcome P9473185QR OTHER", "amount": 346.92, "direction": "debit", "balance": 169649.53, "account_id": "acc-usd-savings"},
            {"date": "2025-09-27", "description": "Fps credit FPS TRANSFER 6073478 TO: HKIRD OTHER", "amount": 631.17, "direction": "credit", "balance": 170280.70, "account_id": "acc-usd-savings"},
            {"date": "2025-09-30", "description": "Fps payment FASTER PAYMENT 8134726 TO: Smartone HK OTHER", "amount": 129.85, "direction": "debit", "balance": 170150.85, "account_id": "acc-usd-savings"}
        ]
    }
    with open(os.path.join(GROUND_TRUTH_DIR, "bsb-004.json"), "w", encoding="utf-8") as f:
        json.dump(gt_bsb004, f, indent=2)

    # 5. bsb-005 (Harbour Bank - Canada)
    gt_bsb005 = {
        "statement_id": "bsb-005",
        "bank": "Harbour Bank",
        "country": "CA",
        "currency": "CAD",
        "opening_balance": 10750.00,
        "closing_balance": 11133.60,
        "total_debits": 6886.21,
        "total_credits": 7269.81,
        "transactions": [
            {"date": "2025-01-02", "description": "SKIP PLATS", "amount": 151.30, "direction": "debit", "balance": 10598.70},
            {"date": "2025-01-02", "description": "DEPOT DIRECT SALAIRE", "amount": 10.33, "direction": "credit", "balance": 10609.03},
            {"date": "2025-01-03", "description": "AMAZON.CA", "amount": 1200.45, "direction": "debit", "balance": 9408.58},
            {"date": "2025-01-06", "description": "DEPOT PAIE", "amount": 101.15, "direction": "credit", "balance": 9509.73},
            {"date": "2025-01-06", "description": "PETRO-CANADA", "amount": 29.69, "direction": "debit", "balance": 9480.04},
            {"date": "2025-01-06", "description": "SPOTIFY CA", "amount": 541.27, "direction": "debit", "balance": 8938.77},
            {"date": "2025-01-07", "description": "METRO EPICERIE", "amount": 712.20, "direction": "debit", "balance": 8226.57},
            {"date": "2025-01-09", "description": "PHARMAPRIX", "amount": 323.62, "direction": "debit", "balance": 7902.95},
            {"date": "2025-01-09", "description": "HYDRO-QUEBEC", "amount": 588.27, "direction": "debit", "balance": 7314.68},
            {"date": "2025-01-11", "description": "CANADIAN TIRE", "amount": 18.70, "direction": "debit", "balance": 7295.98},
            {"date": "2025-01-12", "description": "MAGASIN VÊTEMENTS", "amount": 100.28, "direction": "debit", "balance": 7195.70},
            {"date": "2025-01-12", "description": "INTERETS GAGNES", "amount": 31.46, "direction": "credit", "balance": 7227.16},
            {"date": "2025-01-13", "description": "DEPOT DIRECT SALAIRE", "amount": 33.97, "direction": "credit", "balance": 7261.13},
            {"date": "2025-01-14", "description": "STM MONTREAL", "amount": 567.79, "direction": "debit", "balance": 6693.34},
            {"date": "2025-01-14", "description": "VIREMENT INTERAC RECU", "amount": 66.64, "direction": "credit", "balance": 6759.98},
            {"date": "2025-01-16", "description": "STARBUCKS CAFE", "amount": 84.98, "direction": "debit", "balance": 6675.00},
            {"date": "2025-01-16", "description": "VIREMENT ELECTRONIQUE RECU", "amount": 125.28, "direction": "credit", "balance": 6800.28},
            {"date": "2025-01-19", "description": "TIM HORTONS", "amount": 72.92, "direction": "debit", "balance": 6727.36},
            {"date": "2025-01-20", "description": "DEPOT PAIE", "amount": 6900.98, "direction": "credit", "balance": 13628.34},
            {"date": "2025-01-21", "description": "UBER COURSE", "amount": 1895.80, "direction": "debit", "balance": 11732.54},
            {"date": "2025-01-23", "description": "LA BAIE", "amount": 88.96, "direction": "debit", "balance": 11643.58},
            {"date": "2025-01-24", "description": "TIM HORTONS", "amount": 53.50, "direction": "debit", "balance": 11590.08},
            {"date": "2025-01-25", "description": "APPLE.COM/BILL", "amount": 17.26, "direction": "debit", "balance": 11572.82},
            {"date": "2025-01-26", "description": "GAZ METRO", "amount": 422.11, "direction": "debit", "balance": 11150.71},
            {"date": "2025-01-26", "description": "NETFLIX.COM", "amount": 17.11, "direction": "debit", "balance": 11133.60}
        ]
    }
    with open(os.path.join(GROUND_TRUTH_DIR, "bsb-005.json"), "w", encoding="utf-8") as f:
        json.dump(gt_bsb005, f, indent=2)

    # 6. bank_muscat (Synthetic Bank Muscat Sample)
    gt_bank_muscat = {
        "statement_id": "bank_muscat",
        "bank": "Bank Muscat",
        "country": "OM",
        "currency": "OMR",
        "opening_balance": 1500.000,
        "closing_balance": 2199.500,
        "total_debits": 221.500,
        "total_credits": 921.000,
        "transactions": [
            {"date": "2025-01-02", "description": "SALARY CREDIT PETROLEUM DEV OMAN EMPLOYEE ID PDO-99120", "amount": 850.500, "direction": "credit", "balance": 2350.500},
            {"date": "2025-01-05", "description": "ATM CASH WITHDRAWAL MUSCAT GRAND MALL ATM", "amount": 50.000, "direction": "debit", "balance": 2300.500},
            {"date": "2025-01-10", "description": "POS PURCHASE LULU HYPERMARKET BAUSHER STORE 12", "amount": 45.250, "direction": "debit", "balance": 2255.250},
            {"date": "2025-01-15", "description": "UTILITY BILL PAYMENT OMANTEL ACCOUNT 96899128", "amount": 25.750, "direction": "debit", "balance": 2229.500},
            {"date": "2025-01-20", "description": "FUNDS TRANSFER TO SALIM AL-BALUSHI FAMILY SUPPORT PAYMENT", "amount": 100.000, "direction": "debit", "balance": 2129.500},
            {"date": "2025-01-25", "description": "DIVIDEND CREDIT OMINVEST SECURITIES ANNUAL DISTRIBUTION 2024", "amount": 70.500, "direction": "credit", "balance": 2200.000},
            {"date": "2025-01-31", "description": "MONTHLY SERVICE FEE ACCOUNT MAINTENANCE CHARGE", "amount": 0.500, "direction": "debit", "balance": 2199.500}
        ]
    }
    with open(os.path.join(GROUND_TRUTH_DIR, "bank_muscat.json"), "w", encoding="utf-8") as f:
        json.dump(gt_bank_muscat, f, indent=2)

    print("All 6 ground-truth reference files successfully generated in:", GROUND_TRUTH_DIR)


if __name__ == "__main__":
    build_all_ground_truth()
