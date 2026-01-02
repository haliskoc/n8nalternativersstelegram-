#!/bin/bash

# RSS Telegram Bot - Unified CLI Manager
# This script acts as the main entry point for the application.

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Resolve Project Directory
# This ensures the script works even when called from a symlink in /usr/local/bin
SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
PROJECT_DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )

cd "$PROJECT_DIR" || exit 1

# Check for root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This application requires root privileges to manage Docker and system files.${NC}"
   echo "Please run with sudo: sudo rsstelegram"
   exit 1
fi

# Helper Functions
pause() {
    read -p "Press Enter to continue..."
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker not found! Please install Docker.${NC}"
        return 1
    fi
    return 0
}

get_compose_cmd() {
    if docker compose version &> /dev/null; then
        echo "docker compose"
    else
        echo "docker-compose"
    fi
}

COMPOSE_CMD=$(get_compose_cmd)

# Menu Functions
show_status() {
    echo -e "\n${BLUE}--- Bot Status ---${NC}"
    if docker ps | grep -q "rss-telegram-bot"; then
        echo -e "Status: ${GREEN}RUNNING${NC}"
        echo "Uptime: $(docker ps -f name=rss-telegram-bot --format "{{.Status}}")"
    else
        echo -e "Status: ${RED}STOPPED${NC}"
    fi
    echo "------------------"
}

manage_feeds() {
    ./update_feeds.sh
}

manage_opml() {
    while true; do
        clear
        echo -e "${BLUE}=== OPML Import/Export ===${NC}"
        echo "1. Import OPML File"
        echo "2. Export Feeds to OPML"
        echo "0. Back to Main Menu"
        echo "--------------------------"
        read -p "Choice: " opml_choice
        
        case $opml_choice in
            1)
                read -p "Enter full path to .opml file: " opml_path
                if [ -f "$opml_path" ]; then
                    python3 opml_manager.py import "$opml_path"
                    echo -e "${YELLOW}Note: You may need to go to 'Manage Feeds' to select the newly imported feeds.${NC}"
                else
                    echo -e "${RED}File not found!${NC}"
                fi
                pause
                ;;
            2)
                read -p "Enter output filename (default: feeds_export.opml): " opml_out
                if [[ -z "$opml_out" ]]; then opml_out="feeds_export.opml"; fi
                python3 opml_manager.py export "$opml_out"
                pause
                ;;
            0) return ;;
            *) echo "Invalid choice"; pause ;;
        esac
    done
}

bot_control() {
    while true; do
        clear
        show_status
        echo -e "${BLUE}=== Bot Control ===${NC}"
        echo "1. Start Bot"
        echo "2. Stop Bot"
        echo "3. Restart Bot"
        echo "4. View Live Logs"
        echo "0. Back to Main Menu"
        echo "-------------------"
        read -p "Choice: " ctrl_choice
        
        case $ctrl_choice in
            1)
                echo "Starting bot..."
                $COMPOSE_CMD up -d --build
                pause
                ;;
            2)
                echo "Stopping bot..."
                $COMPOSE_CMD stop
                pause
                ;;
            3)
                echo "Restarting bot..."
                $COMPOSE_CMD restart
                pause
                ;;
            4)
                echo -e "${YELLOW}Press Ctrl+C to exit logs${NC}"
                sleep 1
                $COMPOSE_CMD logs -f
                ;;
            0) return ;;
            *) echo "Invalid choice"; pause ;;
        esac
    done
}

settings_menu() {
    while true; do
        clear
        echo -e "${BLUE}=== Settings ===${NC}"
        echo "Current Configuration (.env):"
        if [ -f .env ]; then
            # Show non-sensitive info or masked info
            echo "----------------"
            grep -v "KEY" .env | grep -v "TOKEN"
            echo "TOKEN=********"
            echo "KEY=********"
            echo "----------------"
        else
            echo -e "${RED}.env file not found!${NC}"
        fi
        
        echo -e "\n1. Edit .env file (nano)"
        echo "2. Re-run Setup Wizard"
        echo "0. Back to Main Menu"
        echo "----------------"
        read -p "Choice: " set_choice
        
        case $set_choice in
            1)
                if command -v nano &> /dev/null; then
                    nano .env
                    echo -e "${YELLOW}You must restart the bot for changes to take effect.${NC}"
                else
                    echo "nano editor not found. Opening in vi..."
                    vi .env
                fi
                pause
                ;;
            2)
                ./setup.sh
                return # Setup script might exit or change state significantly
                ;;
            0) return ;;
            *) echo "Invalid choice"; pause ;;
        esac
    done
}

# Main Loop
while true; do
    clear
    echo -e "${BLUE}====================================${NC}"
    echo -e "${BLUE}   RSS Telegram Bot Manager v1.0    ${NC}"
    echo -e "${BLUE}====================================${NC}"
    
    show_status
    
    echo "1. 📰 Manage Feeds (Add/Remove/Search)"
    echo "2. 🔄 Import/Export OPML"
    echo "3. 🤖 Bot Control (Start/Stop/Logs)"
    echo "4. ⚙️  Settings & Configuration"
    echo "5. ⬆️  Update Application"
    echo "6. 🗑️  Uninstall Project"
    echo "0. 🚪 Exit"
    echo "------------------------------------"
    read -p "Select an option: " main_choice
    
    case $main_choice in
        1) manage_feeds ;;
        2) manage_opml ;;
        3) bot_control ;;
        4) settings_menu ;;
        5) 
            echo "Updating..."
            ./update.sh
            pause
            ;;
        6)
            ./uninstall.sh
            exit 0
            ;;
        0) 
            echo "Goodbye!"
            exit 0
            ;;
        *) 
            echo "Invalid option."
            pause
            ;;
    esac
done
