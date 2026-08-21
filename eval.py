import time, json
from pydantic import ValidationError
from schema import Postmortem
from pipeline_local import call_model, call_model_local

def evaluate(name, call_fn, test_set):
    passed, latencies = 0, []
    for ex in test_set:
        start = time.time()
        raw = call_fn(ex["transcript"])
        elapsed = time.time() - start
        latencies.append(elapsed)
        print(f"  {name}: {elapsed:.1f}s")  # <-- add this
        try:
            Postmortem(**json.loads(raw))
            passed += 1
        except (json.JSONDecodeError, ValidationError):
            pass
    n = len(test_set)
    return {
        "model": name,
        "json_pass_rate": round(100 * passed / n, 1),
        "avg_latency_s": round(sum(latencies) / n, 2),
    }

if __name__ == "__main__":
    test_set = [json.loads(l) for l in open("data/incident_test.jsonl")]
    results = [
        evaluate("base (hosted API)", call_model, test_set),
        evaluate("fine-tuned (local)", call_model_local, test_set),
    ]
    import csv
    with open("eval_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=results[0].keys())
        w.writeheader()
        w.writerows(results)
    print(results)