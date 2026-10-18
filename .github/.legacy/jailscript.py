import re
import json

def to_dashed(uuid):
    """Return the UUID in Minecraft's dashed format, matching the playerdata filenames."""
    clean = uuid.replace("-", "").lower()
    if len(clean) != 32:
        return uuid
    return f"{clean[:8]}-{clean[8:12]}-{clean[12:16]}-{clean[16:20]}-{clean[20:]}"

def parse_sql_to_json(sql_input):
    whitelist = ["UT_Austin", "HaloODST", "cheribumie"]
    pattern = re.compile(r"INSERT INTO PUNISHMENTS VALUES\(\d+,'([^']+)','([^']+)','[^']+','[^']+','[^']+',(\d+),-1,'[^']*'\)")
    matches = pattern.findall(sql_input)
    
    punishments = []
    for match in matches:
        name, uuid, punishment_date = match
        if name in whitelist:
            continue
        punishment = {
            "name": name,
            "uuid": to_dashed(uuid),
            "punishmentDate": int(punishment_date)
        }
        punishments.append(punishment)
    
    return json.dumps(punishments, indent=2)

if __name__ == "__main__":
    print("ENTER LINE HERE:")
    sql_input = ""
    while True:
        line = input()
        if line == "":
            break
        sql_input += line + "\n"

    json_output = parse_sql_to_json(sql_input)
    print(json_output)