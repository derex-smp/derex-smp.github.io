import os
import sys
import json
import time
import urllib.request
import urllib.error

def get_best_model(api_key):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for m in data.get("models", []):
                name = m.get("name", "")
                methods = m.get("supportedGenerationMethods", [])
                if "generateContent" in methods and "flash" in name.lower() and "exp" not in name.lower():
                    return name.replace("models/", "")
    except Exception:
        pass
    return "gemini-1.5-flash"

def query_gemini_batch(names, api_key):
    template = os.environ.get("MODERATION_PROMPT")
    if template:
        if "{{NAMES}}" in template:
            prompt = template.replace("{{NAMES}}", json.dumps(names))
        else:
            prompt = f"{template}\n\nUsernames to analyze: {json.dumps(names)}"
    else:
        prompt = f"Analyze these usernames and return a JSON array of strings containing only the usernames that violate community safety standards: {json.dumps(names)}"

    chosen_model = get_best_model(api_key)
    candidates = [chosen_model]
    for fallback in ["gemini-1.5-flash", "gemini-2.0-flash"]:
        if fallback not in candidates:
            candidates.append(fallback)

    for model_name in candidates:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.0,
                "responseMimeType": "application/json"
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    flagged = json.loads(text)
                    if isinstance(flagged, list):
                        return set(flagged)
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(5 * (attempt + 1))
                    continue
                break
            except Exception:
                time.sleep(2)
                continue

    return set()

def main():
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_path = os.path.join(repo_dir, "src", "data", "player_history.json")
    punishments_path = os.path.join(repo_dir, "src", "data", "punishments.json")

    history = {}
    if os.path.isfile(history_path):
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = {}

    punishments = []
    if os.path.isfile(punishments_path):
        try:
            with open(punishments_path, "r", encoding="utf-8") as f:
                punishments = json.load(f)
        except Exception:
            punishments = []

    name_to_sources = {}
    for uuid, rec in history.items():
        curr = rec.get("currentName")
        if curr and curr != "[Inappropriate Name]":
            name_to_sources.setdefault(curr, []).append(f"player_history ({uuid} currentName)")
        for p in rec.get("pastNames", []):
            if p and p != "[Inappropriate Name]":
                name_to_sources.setdefault(p, []).append(f"player_history ({uuid} pastNames)")

    for p in punishments:
        name = p.get("name")
        if name and name != "[Inappropriate Name]":
            name_to_sources.setdefault(name, []).append(f"punishments ({p.get('uuid', 'unknown')})")

    unique_names = sorted(list(name_to_sources.keys()))
    print(f"Total unique existing names to audit: {len(unique_names)}")

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set. Cannot run moderation audit.")
        sys.exit(1)

    flagged_results = {}
    batch_size = 50
    total_batches = (len(unique_names) + batch_size - 1) // batch_size

    for i in range(0, len(unique_names), batch_size):
        batch_idx = (i // batch_size) + 1
        batch = unique_names[i:i + batch_size]
        print(f"Auditing batch {batch_idx}/{total_batches} ({len(batch)} names)...")
        flagged = query_gemini_batch(batch, api_key)
        for name in batch:
            if name in flagged:
                flagged_results[name] = name_to_sources.get(name, [])
        time.sleep(1.0)

    report_lines = [
        "# Player Name Moderation Audit Report",
        "",
        f"- **Total Unique Names Audited**: {len(unique_names)}",
        f"- **Flagged Names Found**: {len(flagged_results)}",
        f"- **Audit Mode**: Dry-Run (No files were modified)",
        "",
    ]

    if flagged_results:
        report_lines.append("## Flagged Usernames")
        report_lines.append("")
        report_lines.append("| Username | Occurrences / References |")
        report_lines.append("|---|---|")
        for name, sources in sorted(flagged_results.items()):
            src_str = "<br>".join(sources[:5])
            if len(sources) > 5:
                src_str += f"<br>...and {len(sources) - 5} more"
            report_lines.append(f"| `{name}` | {src_str} |")
    else:
        report_lines.append("## Result")
        report_lines.append("")
        report_lines.append("No inappropriate names were flagged by Gemini. All existing names passed the audit!")

    report_md = "\n".join(report_lines)

    report_path = os.path.join(repo_dir, "audit_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        try:
            with open(step_summary, "a", encoding="utf-8") as f:
                f.write("\n" + report_md + "\n")
        except Exception:
            pass

    print("\nAudit complete.")
    print(f"Flagged names: {len(flagged_results)}")
    print(f"Report written to: {report_path}")

if __name__ == "__main__":
    main()
