"""
Real Batch Test — Uses Docker API with REAL ML model
No mocks, no fallbacks, 100% genuine predictions
"""

import json
import time
import requests
from pathlib import Path

API_URL = "http://localhost:8000/api/analyze"
SAMPLE_SIZE = 20

def analyze(filepath):
    with open(filepath, "rb") as f:
        resp = requests.post(API_URL, files={"file": ("email.eml", f, "message/rfc822")}, timeout=30)
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"HTTP {resp.status_code}"}

def classify(result):
    if "error" in result:
        return "error"
    ml = result.get("nlp", {}).get("ml_phishing_probability", 0)
    sc = result.get("risk_score", {}).get("total_score", 0)
    if ml > 0.7 or sc >= 40:
        return "phishing"
    return "legitimate"

def main():
    base = Path(__file__).parent / "tests" / "fixtures" / "datasets"
    ham = sorted((base / "easy_ham").glob("*"))[:SAMPLE_SIZE]
    spam = sorted((base / "spam").glob("*"))[:SAMPLE_SIZE]

    print(f"\n{'='*65}")
    print(f"  REAL BATCH TEST — Docker + Real ML Model")
    print(f"  {len(ham)} ham + {len(spam)} spam emails")
    print(f"  NO MOCKS — All predictions are genuine")
    print(f"{'='*65}\n")

    # HAM
    h_c, h_i, h_s, h_ml = 0, 0, [], []
    t0 = time.time()
    for i, fp in enumerate(ham):
        r = analyze(str(fp))
        p = classify(r)
        sc = r.get("risk_score", {}).get("total_score", 0)
        ml = r.get("nlp", {}).get("ml_phishing_probability", 0)
        h_s.append(sc)
        h_ml.append(ml)
        if p == "legitimate": h_c += 1
        else: h_i += 1
        if (i + 1) % 10 == 0:
            print(f"  HAM: {i+1}/{len(ham)} ({time.time()-t0:.1f}s)")
    ht = time.time() - t0

    # SPAM
    s_c, s_i, s_s, s_ml = 0, 0, [], []
    t0 = time.time()
    for i, fp in enumerate(spam):
        r = analyze(str(fp))
        p = classify(r)
        sc = r.get("risk_score", {}).get("total_score", 0)
        ml = r.get("nlp", {}).get("ml_phishing_probability", 0)
        s_s.append(sc)
        s_ml.append(ml)
        if p == "phishing": s_c += 1
        else: s_i += 1
        if (i + 1) % 10 == 0:
            print(f"  SPAM: {i+1}/{len(spam)} ({time.time()-t0:.1f}s)")
    st = time.time() - t0

    total = len(ham) + len(spam)
    tc = h_c + s_c
    ti = h_i + s_i
    acc = tc / (tc + ti) * 100
    ha = h_c / len(ham) * 100
    sa = s_c / len(spam) * 100

    print(f"\n{'='*65}")
    print(f"  REAL ACCURACY REPORT (Docker + Real ML)")
    print(f"{'='*65}")
    print(f"\n  OVERALL: {tc}/{total} correct = {acc:.1f}% accuracy")
    print(f"  Time: {ht+st:.1f}s ({(ht+st)/total:.1f}s per email)")
    print(f"\n  HAM:  {h_c}/{len(ham)} correct = {ha:.1f}% | avg score {sum(h_s)/len(h_s):.1f} | avg ML {sum(h_ml)/len(h_ml):.4f}")
    print(f"  SPAM: {s_c}/{len(spam)} correct = {sa:.1f}% | avg score {sum(s_s)/len(s_s):.1f} | avg ML {sum(s_ml)/len(s_ml):.4f}")

    # False positives/negatives
    if h_i > 0:
        print(f"\n  FALSE POSITIVES ({h_i}):")
        cnt = 0
        for i, fp in enumerate(ham):
            r = analyze(str(fp))
            if classify(r) == "phishing":
                ml = r.get("nlp", {}).get("ml_phishing_probability", 0)
                sc = r.get("risk_score", {}).get("total_score", 0)
                print(f"    - {fp.name}: score={sc}, ml={ml:.4f}")
                cnt += 1
                if cnt >= 3: break

    if s_i > 0:
        print(f"\n  FALSE NEGATIVES ({s_i}):")
        cnt = 0
        for i, fp in enumerate(spam):
            r = analyze(str(fp))
            if classify(r) == "legitimate":
                ml = r.get("nlp", {}).get("ml_phishing_probability", 0)
                sc = r.get("risk_score", {}).get("total_score", 0)
                print(f"    - {fp.name}: score={sc}, ml={ml:.4f}")
                cnt += 1
                if cnt >= 3: break

    # Score distribution
    print(f"\n  SCORE DISTRIBUTION:")
    print(f"  {'Range':<10} {'HAM':>6} {'SPAM':>6}")
    print(f"  {'-'*24}")
    for lo, hi in [(0,20),(21,40),(41,60),(61,80),(81,100)]:
        hc = sum(1 for s in h_s if lo <= s <= hi)
        sc = sum(1 for s in s_s if lo <= s <= hi)
        print(f"  {lo:>3}-{hi:<3}   {hc:>5}  {sc:>5}")

    print(f"\n  ML PROBABILITY DISTRIBUTION:")
    print(f"  {'Range':<10} {'HAM':>6} {'SPAM':>6}")
    print(f"  {'-'*24}")
    for lo, hi in [(0,0.2),(0.2,0.4),(0.4,0.6),(0.6,0.8),(0.8,1.0)]:
        hc = sum(1 for m in h_ml if lo <= m < hi)
        sc = sum(1 for m in s_ml if lo <= m < hi)
        print(f"  {lo:.1f}-{hi:.1f}    {hc:>5}  {sc:>5}")

    print(f"\n{'='*65}\n")

    report = {
        "test_type": "REAL (Docker + Real ML Model)",
        "sample_size": SAMPLE_SIZE,
        "total": total,
        "accuracy": round(acc, 1),
        "time_seconds": round(ht + st, 1),
        "ham": {"total": len(ham), "correct": h_c, "incorrect": h_i, "accuracy": round(ha, 1), "avg_score": round(sum(h_s)/len(h_s), 1), "avg_ml": round(sum(h_ml)/len(h_ml), 4)},
        "spam": {"total": len(spam), "correct": s_c, "incorrect": s_i, "accuracy": round(sa, 1), "avg_score": round(sum(s_s)/len(s_s), 1), "avg_ml": round(sum(s_ml)/len(s_ml), 4)},
    }
    with open(Path(__file__).parent / "tests" / "real_batch_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"  Report saved: backend/tests/real_batch_report.json")

if __name__ == "__main__":
    main()
