import os
import re

ROOT_DIR = "aweomsrss/awesome-rss-feeds"
OUTPUT_FILE = "feeds_db.txt"

def parse_opml_regex(filepath):
    feeds = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Regex to find outline tags with xmlUrl
        # This is a bit rough but should work for standard OPML
        # We look for <outline ... xmlUrl="..." ... >
        # We also want to capture text="..." or title="..."
        
        # Pattern explanation:
        # <outline\s+              : start of tag
        # (?:[^>]*?\s+)?           : optional other attributes
        # (?:text|title)=["'](.*?)["'] : capture name (group 1)
        # (?:[^>]*?\s+)?           : optional other attributes
        # xmlUrl=["'](.*?)["']     : capture url (group 2)
        
        # Since attributes can be in any order, we might need to find all outlines and then extract attributes
        outline_pattern = re.compile(r'<outline\s+([^>]+)>')
        
        for match in outline_pattern.finditer(content):
            attrs_str = match.group(1)
            
            # Extract xmlUrl
            url_match = re.search(r'xmlUrl=["\'](.*?)["\']', attrs_str)
            if not url_match:
                continue
            url = url_match.group(1)
            
            # Extract text or title
            name_match = re.search(r'(?:text|title)=["\'](.*?)["\']', attrs_str)
            name = name_match.group(1) if name_match else "Unknown Feed"
            
            feeds.append((name, url))
            
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    return feeds

all_feeds = []

# 1. Process Countries
countries_dir = os.path.join(ROOT_DIR, "countries", "with_category")
if os.path.exists(countries_dir):
    for filename in os.listdir(countries_dir):
        if filename.endswith(".opml"):
            filepath = os.path.join(countries_dir, filename)
            country_name = os.path.splitext(filename)[0]
            feeds = parse_opml_regex(filepath)
            for name, url in feeds:
                all_feeds.append((f"Country: {country_name}", name, url))

# 2. Process Recommended (Topics)
recommended_dir = os.path.join(ROOT_DIR, "recommended", "with_category")
if os.path.exists(recommended_dir):
    for filename in os.listdir(recommended_dir):
        if filename.endswith(".opml"):
            filepath = os.path.join(recommended_dir, filename)
            topic_name = os.path.splitext(filename)[0]
            feeds = parse_opml_regex(filepath)
            for name, url in feeds:
                all_feeds.append((f"Topic: {topic_name}", name, url))

# Sort by Category then Name
all_feeds.sort(key=lambda x: (x[0], x[1]))

# Write to file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for cat, name, url in all_feeds:
        # Sanitize
        name = name.replace("|", "-").strip()
        cat = cat.replace("|", "-").strip()
        url = url.strip()
        f.write(f"{cat}|{name}|{url}\n")

print(f"Generated {len(all_feeds)} feeds in {OUTPUT_FILE}")
