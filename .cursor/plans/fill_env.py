#!/usr/bin/env python3
import os, re, json, argparse
try:
    import boto3
except Exception:
    boto3 = None

PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")

def load_json(path):
    with open(path,'r',encoding='utf-8') as f: return json.load(f)

def fetch_aws(secret_name, json_key=None):
    if boto3 is None:
        raise RuntimeError("boto3 required for AWS Secrets Manager access")
    client = boto3.client("secretsmanager")
    resp = client.get_secret_value(SecretId=secret_name)
    s = resp.get("SecretString")
    try:
        obj = json.loads(s)
    except Exception:
        obj = None
    return str(obj.get(json_key)) if (obj and json_key) else s

def resolve(k, mapping, secrets_json):
    if k in mapping:
        spec = mapping[k]
        src = spec.get("source","env")
        if src == "env":
            return os.environ.get(spec.get("env_var", k))
        if src == "json":
            file = spec["file"]
            j = load_json(file)
            return j.get(spec.get("key", k))
        if src == "aws":
            return fetch_aws(spec["secret_name"], spec.get("json_key"))
        raise RuntimeError(f"Unknown source {src}")
    # fallback env
    if os.environ.get(k):
        return os.environ.get(k)
    # fallback secrets.json
    if secrets_json and k in secrets_json:
        return secrets_json[k]
    return None

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-t","--template", default=".env.template")
    p.add_argument("-o","--out", default=".env")
    p.add_argument("-m","--mapping", help="mapping.json optional")
    p.add_argument("-s","--secrets", help="secrets.json optional")
    args = p.parse_args()

    mapping = json.load(open(args.mapping)) if args.mapping else {}
    secrets = json.load(open(args.secrets)) if args.secrets else {}

    tpl = open(args.template,"r",encoding="utf-8").read()
    keys = set(PLACEHOLDER_RE.findall(tpl))
    vals = {}
    missing = []
    for k in keys:
        v = resolve(k, mapping, secrets)
        if v is None:
            missing.append(k)
        else:
            vals[k] = v

    if missing:
        print("ERROR: faltan valores para:", missing)
        return 2

    out = PLACEHOLDER_RE.sub(lambda m: vals[m.group(1)], tpl)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(out)
    os.chmod(args.out, 0o600)
    print(f".env creado: {args.out} (perm 600)")

if __name__=="__main__":
    main()
