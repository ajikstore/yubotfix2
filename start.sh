#!/bin/bash

RED='\033[38;2;255;0;0m'
GREEN='\033[38;2;0;255;0m'
BLUE='\033[38;2;0;150;255m'
PURPLE='\033[38;2;180;0;255m'
CYAN='\033[38;2;0;255;255m'
YELLOW='\033[38;2;255;255;0m'
RESET='\033[0m'

echo -e "${PURPLE}╔══════════════════════════════════════╗${RESET}"
echo -e "${BLUE}║                                      ║${RESET}"
echo -e "${CYAN}║        🚀 GARFIELD USERBOT 🚀           ║${RESET}"
echo -e "${BLUE}║                                      ║${RESET}"
echo -e "${PURPLE}╠══════════════════════════════════════╣${RESET}"
echo -e "${YELLOW}║   SABAR LOADING KNTL   ║${RESET}"
echo -e "${PURPLE}╚══════════════════════════════════════╝${RESET}"
echo ""

sleep 1

echo -e "${GREEN}🔄 Cleaning session...${RESET}"
rm -rf *session

sleep 1

echo -e "${CYAN}🚀 Menjalankan bot...${RESET}"
sleep 1

python3 -m kelra
