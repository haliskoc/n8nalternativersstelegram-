#!/usr/bin/env python3
import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

FEEDS_FILE = 'feeds.json'

def load_feeds():
    if os.path.exists(FEEDS_FILE):
        try:
            with open(FEEDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading feeds.json: {e}")
            return []
    return []

def save_feeds(feeds):
    try:
        with open(FEEDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(feeds, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving feeds.json: {e}")
        return False

def import_opml(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        new_feeds = []
        # Find all outline elements with xmlUrl attribute
        # OPML structure can be nested, so we search recursively
        for outline in root.findall('.//outline[@xmlUrl]'):
            url = outline.get('xmlUrl')
            if url:
                new_feeds.append(url)
        
        if not new_feeds:
            print("No RSS feeds found in OPML file.")
            return

        current_feeds = load_feeds()
        initial_count = len(current_feeds)
        
        # Add only unique feeds
        added_count = 0
        for feed in new_feeds:
            if feed not in current_feeds:
                current_feeds.append(feed)
                added_count += 1
        
        if added_count > 0:
            if save_feeds(current_feeds):
                print(f"Successfully imported {added_count} new feeds.")
                print(f"Total feeds: {len(current_feeds)}")
            else:
                print("Failed to save feeds.")
        else:
            print("No new feeds to import (all already exist).")
            
    except ET.ParseError:
        print("Error: Invalid OPML/XML file format.")
    except Exception as e:
        print(f"Error importing OPML: {e}")

def export_opml(output_path):
    feeds = load_feeds()
    if not feeds:
        print("No feeds to export.")
        return

    try:
        # Create OPML structure
        opml = ET.Element('opml', version="1.0")
        head = ET.SubElement(opml, 'head')
        title = ET.SubElement(head, 'title')
        title.text = "RSS Feeds Export"
        date_created = ET.SubElement(head, 'dateCreated')
        date_created.text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

        body = ET.SubElement(opml, 'body')
        
        for feed_url in feeds:
            # We don't have titles in feeds.json, so we use the URL as title
            ET.SubElement(body, 'outline', 
                          text=feed_url, 
                          title=feed_url, 
                          type="rss", 
                          xmlUrl=feed_url)

        # Generate string
        tree = ET.ElementTree(opml)
        ET.indent(tree, space="  ", level=0)
        
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        print(f"Successfully exported {len(feeds)} feeds to {output_path}")
        
    except Exception as e:
        print(f"Error exporting OPML: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 opml_manager.py [import|export] [filename]")
        return

    action = sys.argv[1]
    
    if action == "import":
        if len(sys.argv) < 3:
            print("Usage: python3 opml_manager.py import <file.opml>")
            return
        import_opml(sys.argv[2])
        
    elif action == "export":
        filename = "feeds_export.opml"
        if len(sys.argv) >= 3:
            filename = sys.argv[2]
        export_opml(filename)
        
    else:
        print("Unknown command. Use 'import' or 'export'.")

if __name__ == "__main__":
    main()
