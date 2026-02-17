#!/bin/bash
# Quick Setup Script for Schema Updates

echo "════════════════════════════════════════════════════════════════"
echo "AACS Reviewer System - Schema Update Setup"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Navigate to backend
echo -e "${BLUE}Step 1: Navigating to backend directory...${NC}"
cd backend || exit 1
echo -e "${GREEN}✓ In backend directory${NC}"
echo ""

# Step 2: Run migration
echo -e "${BLUE}Step 2: Running database migration...${NC}"
python add_review_fields.py
MIGRATION_STATUS=$?
echo ""

if [ $MIGRATION_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Migration completed successfully${NC}"
else
    echo -e "${YELLOW}⚠ Migration encountered an issue. Check the output above.${NC}"
    exit 1
fi
echo ""

# Step 3: Show next steps
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ Schema Update Complete!${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Next Steps:"
echo "1. Verify the database changes:"
echo "   mysql -u root aacsjour_aacs -e 'DESCRIBE online_review;'"
echo ""
echo "2. Restart the backend server:"
echo "   python -m uvicorn app.main:app --reload"
echo ""
echo "3. Test the endpoints:"
echo "   - GET /api/v1/reviewer/dashboard/stats"
echo "   - GET /api/v1/reviewer/assignments"
echo ""
echo "Documentation:"
echo "  - SCHEMA_UPDATE_SUMMARY.md - Overview and quick start"
echo "  - SCHEMA_SETUP.md - Detailed setup instructions"
echo "  - SCHEMA_REFERENCE.md - Complete database reference"
echo "  - SCHEMA_CHANGES.md - Technical change details"
echo ""
echo "════════════════════════════════════════════════════════════════"
