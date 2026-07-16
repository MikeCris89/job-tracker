import re

def normalize_slug(raw: str):
    s = raw.lower().strip()
    s = re.sub(r"\.(js|css|ts)$", "", s)   # strip framework suffixes
    s = re.sub(r"[\s.]+", "-", s)          # spaces and dots -> dash
    s = re.sub(r"[^a-z0-9+#-]", "", s)     # keep alnum, +, #, dash
    s = s.strip("-")                       # trim leading/trailing dashes
    return s