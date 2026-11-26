import os
import sys
import json
import urllib.request
import urllib.error

def query_gemini_batch(names, api_key):
    template = os.environ.get("MODERATION_PROMPT")
    if template:
        if "{{NAMES}}" in template:
            prompt = template.replace("{{NAMES}}", json.dumps(names))
        else:
            prompt = f"{template}\n\nUsernames to analyze: {json.dumps(names)}"
    else:
        prompt = f"Analyze these usernames and return a JSON array of strings containing only the usernames that violate community safety standards: {json.dumps(names)}"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
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
    except Exception as e:
        print(f"Gemini API request failed: {e}", file=sys.stderr)

    return set()

def main():
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reviewed_path = os.path.join(repo_dir, "src", "data", "reviewed_names.json")
    history_path = os.path.join(repo_dir, "src", "data", "player_history.json")
    punishments_path = os.path.join(repo_dir, "src", "data", "punishments.json")

    reviewed = set()
    if os.path.isfile(reviewed_path):
        try:
            with open(reviewed_path, "r", encoding="utf-8") as f:
                reviewed = set(json.load(f))
        except Exception:
            reviewed = set()

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

    unreviewed = [n for n in all_names if n not in reviewed]

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("API_KEY")
    flagged_names = set()
    if api_key and unreviewed:
        print(f"Reviewing {len(unreviewed)} unmoderated names with Gemini...")
        batch_size = 50
        for i in range(0, len(unreviewed), batch_size):
            batch = unreviewed[i:i + batch_size]
            batch_flagged = query_gemini_batch(batch, api_key)
            for name in batch:
                if name in batch_flagged:
                    flagged_names.add(name)
                else:
                    reviewed.add(name)

        clean_list = sorted(list(reviewed))
        with open(reviewed_path, "w", encoding="utf-8") as f:
            json.dump(clean_list, f, indent=2)

    history_changed = False
    for rec in history.values():
        curr = rec.get("currentName")
        if curr and curr in flagged_names:
            rec["currentName"] = "[Inappropriate Name]"
            history_changed = True

        past = rec.get("pastNames", [])
        new_past = []
        has_past_change = False
        for p in past:
            if p in flagged_names:
                if "[Inappropriate Name]" not in new_past:
                    new_past.append("[Inappropriate Name]")
                has_past_change = True
            else:
                new_past.append(p)

        if has_past_change:
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
