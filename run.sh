#!/bin/bash
# Quick launcher script for arbitrage scanner

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Polymarket-Kalshi Arbitrage Scanner ===${NC}\n"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo -e "${YELLOW}Please create a .env file with your configuration.${NC}"
    echo "See SETUP.md for instructions."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update requirements
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q -r requirements.txt

# Run the scanner
echo -e "${GREEN}Starting arbitrage scanner...${NC}\n"
python main.py "$@"

