#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     OS_TYPE=Linux;;
    Darwin*)    OS_TYPE=Mac;;
    *)          OS_TYPE="UNKNOWN";;
esac

# Check for root privileges (Only strict on Linux)
if [[ "$OS_TYPE" == "Linux" && $EUID -ne 0 ]]; then
   echo -e "${RED}Bu script sudo (root) yetkisi ile çalıştırılmalıdır.${NC}"
   echo -e "${RED}This script must be run with sudo (root) privileges.${NC}"
   echo "Örn: sudo ./update_feeds.sh"
   exit 1
fi

# Detect OS for sed
if [[ "${OS_TYPE}" == "Mac" ]]; then
    SED_CMD="sed -i ''"
else
    SED_CMD="sed -i"
fi

echo -e "${BLUE}=== RSS FEED MANAGER ===${NC}"

# Generate DB if needed
if [ ! -f feeds_db.txt ]; then
    echo "Generating feed database..."
    python3 generate_feeds_db.py
fi

# Temporary file for selected line numbers
> selected_lines.txt

# Load existing feeds if they exist
if [ -f feeds.json ]; then
    echo "Loading existing feeds..."
    python3 -c "
import json
import os
try:
    if os.path.exists('feeds.json') and os.path.exists('feeds_db.txt'):
        with open('feeds.json', 'r') as f:
            urls = json.load(f)
        with open('feeds_db.txt', 'r') as f:
            db_lines = f.readlines()
        selected = []
        for i, line in enumerate(db_lines, 1):
            parts = line.strip().split('|')
            if len(parts) >= 3 and parts[2] in urls:
                selected.append(str(i))
        if selected:
            with open('selected_lines.txt', 'w') as f:
                f.write('\n'.join(selected) + '\n')
except:
    pass
"
fi

while true; do
    clear
    echo -e "${BLUE}=== RSS FEED MANAGER ===${NC}"
    echo "1) Search Feeds / Haber Kaynağı Ara"
    echo "2) Browse by Category / Kategorilere Göre Gez"
    echo "3) View Selected / Seçilenleri Gör"
    echo "4) Save & Restart Bot / Kaydet ve Botu Yeniden Başlat"
    echo "5) Exit without saving / Kaydetmeden Çık"
    echo "------------------------------------------------"
    read -p "Choice/Seçim: " menu_choice
    
    case $menu_choice in
        1)
            read -p "Search Query/Arama Terimi: " query
            if [[ -n "$query" ]]; then
                echo -e "${BLUE}Results for '$query':${NC}"
                grep -in "$query" feeds_db.txt > search_results.tmp
                
                while true; do
                    i=1
                    declare -a map_lines
                    while IFS= read -r line; do
                        line_num=$(echo "$line" | cut -d: -f1)
                        content=$(echo "$line" | cut -d: -f2-)
                        cat_name=$(echo "$content" | cut -d'|' -f1)
                        feed_name=$(echo "$content" | cut -d'|' -f2)
                        
                        if grep -q "^$line_num$" selected_lines.txt; then
                            mark="[x]"
                            color=$GREEN
                        else
                            mark="[ ]"
                            color=$NC
                        fi
                        
                        printf "${color}%3d. %s %s (%s)${NC}\n" $i "$mark" "$feed_name" "$cat_name"
                        map_lines[$i]=$line_num
                        ((i++))
                    done < search_results.tmp
                    
                    if [[ $i -eq 1 ]]; then
                        echo "No results found."
                        read -p "Press Enter to continue..."
                        break
                    fi
                    
                    echo "------------------------------------------------"
                    read -p "Toggle # (0 to back): " toggle_idx
                    
                    if [[ "$toggle_idx" == "0" || -z "$toggle_idx" ]]; then
                        break
                    elif [[ -n "${map_lines[$toggle_idx]}" ]]; then
                        lnum=${map_lines[$toggle_idx]}
                        if grep -q "^$lnum$" selected_lines.txt; then
                            $SED_CMD "/^$lnum$/d" selected_lines.txt
                        else
                            echo "$lnum" >> selected_lines.txt
                        fi
                    fi
                    clear
                    echo -e "${BLUE}Results for '$query':${NC}"
                done
                rm search_results.tmp
            fi
            ;;
        2)
            cut -d'|' -f1 feeds_db.txt | sort | uniq > categories.tmp
            while true; do
                clear
                echo -e "${BLUE}=== CATEGORIES ===${NC}"
                i=1
                declare -a map_cats
                while IFS= read -r cat; do
                    echo "$i. $cat"
                    map_cats[$i]="$cat"
                    ((i++))
                done < categories.tmp
                
                echo "------------------------------------------------"
                read -p "Select Category # (0 to back): " cat_idx
                
                if [[ "$cat_idx" == "0" || -z "$cat_idx" ]]; then
                    break
                elif [[ -n "${map_cats[$cat_idx]}" ]]; then
                    selected_cat="${map_cats[$cat_idx]}"
                    grep -n "^$selected_cat|" feeds_db.txt > cat_feeds.tmp
                    
                    while true; do
                        clear
                        echo -e "${BLUE}Category: $selected_cat${NC}"
                        j=1
                        declare -a map_lines_cat
                        while IFS= read -r line; do
                            line_num=$(echo "$line" | cut -d: -f1)
                            content=$(echo "$line" | cut -d: -f2-)
                            feed_name=$(echo "$content" | cut -d'|' -f2)
                            
                            if grep -q "^$line_num$" selected_lines.txt; then
                                mark="[x]"
                                color=$GREEN
                            else
                                mark="[ ]"
                                color=$NC
                            fi
                            
                            printf "${color}%3d. %s %s${NC}\n" $j "$mark" "$feed_name"
                            map_lines_cat[$j]=$line_num
                            ((j++))
                        done < cat_feeds.tmp
                        
                        echo "------------------------------------------------"
                        read -p "Toggle # (0 to back, 'a' for all): " toggle_idx
                        
                        if [[ "$toggle_idx" == "0" ]]; then
                            break
                        elif [[ "$toggle_idx" == "a" ]]; then
                            while IFS= read -r line; do
                                lnum=$(echo "$line" | cut -d: -f1)
                                if ! grep -q "^$lnum$" selected_lines.txt; then
                                    echo "$lnum" >> selected_lines.txt
                                fi
                            done < cat_feeds.tmp
                        elif [[ -n "${map_lines_cat[$toggle_idx]}" ]]; then
                            lnum=${map_lines_cat[$toggle_idx]}
                            if grep -q "^$lnum$" selected_lines.txt; then
                                $SED_CMD "/^$lnum$/d" selected_lines.txt
                            else
                                echo "$lnum" >> selected_lines.txt
                            fi
                        fi
                    done
                    rm cat_feeds.tmp
                fi
            done
            rm categories.tmp
            ;;
        3)
            clear
            echo -e "${BLUE}=== SELECTED FEEDS ===${NC}"
            if [ -s selected_lines.txt ]; then
                while IFS= read -r lnum; do
                    line=$(sed "${lnum}q;d" feeds_db.txt)
                    name=$(echo "$line" | cut -d'|' -f2)
                    cat=$(echo "$line" | cut -d'|' -f1)
                    echo "- $name ($cat)"
                done < selected_lines.txt
            else
                echo "No feeds selected."
            fi
            read -p "Press Enter to continue..."
            ;;
        4)
            # Generate JSON
            json_content="["
            first=true
            count=0
            if [ -s selected_lines.txt ]; then
                while IFS= read -r lnum; do
                    line=$(sed "${lnum}q;d" feeds_db.txt)
                    url=$(echo "$line" | cut -d'|' -f3)
                    if [ "$first" = true ]; then first=false; else json_content+=","; fi
                    json_content+="\"$url\""
                    ((count++))
                done < selected_lines.txt
            fi
            json_content+="]"
            echo "$json_content" > feeds.json
            echo -e "${GREEN}Feeds saved to feeds.json ($count feeds)${NC}"
            
            # Restart Docker
            echo -e "${BLUE}Restarting bot to apply changes...${NC}"
            if docker compose version &> /dev/null; then
                docker compose up -d --build
            else
                docker-compose up -d --build
            fi
            echo -e "${GREEN}Done! Bot is updated.${NC}"
            rm selected_lines.txt 2>/dev/null
            exit 0
            ;;
        5)
            rm selected_lines.txt 2>/dev/null
            exit 0
            ;;
    esac
done
