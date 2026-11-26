import os
import sys
import json
import re
import subprocess
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

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                flagged = json.loads(text)
                if isinstance(flagged, list):
                    return set(flagged)
        except Exception:
            continue

    return set()

def get_diff_names(repo_dir, all_known_names):
    diffs = []
    cmds = [
        ["git", "diff", "--staged", "-U0", "src/data/player_history.json", "src/data/punishments.json"],
        ["git", "diff", "-U0", "src/data/player_history.json", "src/data/punishments.json"],
        ["git", "diff", "-U0", "HEAD~1", "HEAD", "src/data/player_history.json", "src/data/punishments.json"]
    ]
    for cmd in cmds:
        try:
            res = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                diffs.append(res.stdout)
        except Exception:
            pass

    combined_diff = "\n".join(diffs)
    candidates = set()
    ignored_keywords = {
        "currentName", "pastNames", "lastUpdated", "name", "reason",
        "operator", "punishmentType", "punishmentDate", "uuid",
        "[Inappropriate Name]"
    }

    for line in combined_diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            matches = re.findall(r'"([^"]+)"', line)
            for m in matches:
                if m not in ignored_keywords and m in all_known_names:
                    candidates.add(m)

    return sorted(list(candidates))

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

    all_names = set()
    for rec in history.values():
        if rec.get("currentName") and rec["currentName"] != "[Inappropriate Name]":
            all_names.add(rec["currentName"])
        for p in rec.get("pastNames", []):
            if p and p != "[Inappropriate Name]":
                all_names.add(p)

    for p in punishments:
        name = p.get("name")
        if name and name != "[Inappropriate Name]":
            all_names.add(name)

    if "--all" in sys.argv:
        names_to_review = sorted(list(all_names))
    else:
        names_to_review = get_diff_names(repo_dir, all_names)

    if not names_to_review:
        print("No new unmoderated names found.")
        return

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("API_KEY")
    if not api_key:
        print("Skipping moderation: GEMINI_API_KEY is not set.")
        return

    flagged_names = set()
    print(f"Reviewing {len(names_to_review)} unmoderated names with Gemini...")
    batch_size = 50
    for i in range(0, len(names_to_review), batch_size):
        batch = names_to_review[i:i + batch_size]
        batch_flagged = query_gemini_batch(batch, api_key)
        for name in batch:
            if name in batch_flagged:
                flagged_names.add(name)

    if not flagged_names:
        print("Name moderation check completed. No inappropriate names found.")
        return

    print(f"Flagged {len(flagged_names)} inappropriate names for censoring.")

    history_changed = False
    for rec in history.values():
        curr = rec.get("currentName")
        if curr and curr in flagged_names:
            rec["currentName"] = "[Inappropriate Name]"
            history_changed = True

        past = rec.get("pastNames", [])
        new_past = []
        seen_inappropriate = False
        past_changed = False
        for p in past:
            if p in flagged_names or p == "[Inappropriate Name]":
                if not seen_inappropriate:
                    new_past.append("[Inappropriate Name]")
                    seen_inappropriate = True
                past_changed = True
            else:
                new_past.append(p)

        if past_changed or len(new_past) != len(past):
            rec["pastNames"] = new_past
            history_changed = True

    if history_changed:
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

    punishments_changed = False
    for p in punishments:
        name = p.get("name")
        if name and name in flagged_names:
            p["name"] = "[Inappropriate Name]"
            punishments_changed = True

    if punishments_changed:
        with open(punishments_path, "w", encoding="utf-8") as f:
            json.dump(punishments, f, indent=2)

    print("Name moderation check completed.")

if __name__ == "__main__":
    main()
