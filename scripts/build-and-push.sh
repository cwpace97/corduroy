#!/bin/bash
# Build and push container images to ECR
# Usage: ./scripts/build-and-push.sh [resort-scraper|snotel|forecast|all]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load AWS region from terraform variables or use default
AWS_REGION="${AWS_REGION:-us-east-1}"
PROJECT_NAME="${PROJECT_NAME:-corduroy}"
AWS_PROFILE="${AWS_PROFILE:-default}"

# ECR repository names
RESORT_REPO="${PROJECT_NAME}-resort-scraper"
SNOTEL_REPO="${PROJECT_NAME}-snotel"
FORECAST_REPO="${PROJECT_NAME}-forecast"
HISTORICAL_WEATHER_REPO="${PROJECT_NAME}-historical-weather"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile "${AWS_PROFILE}" --query Account --output text 2>/dev/null || echo "")

if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo -e "${RED}Error: AWS CLI not configured or not authenticated${NC}"
    echo "Please run: aws configure --profile ${AWS_PROFILE}"
    echo "Or set AWS_PROFILE environment variable: export AWS_PROFILE=your-profile-name"
    exit 1
fi

# ECR repository URLs
RESORT_ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${RESORT_REPO}"
SNOTEL_ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${SNOTEL_REPO}"
FORECAST_ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${FORECAST_REPO}"
HISTORICAL_WEATHER_ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${HISTORICAL_WEATHER_REPO}"

# Function to login to ECR
ecr_login() {
    echo -e "${BLUE}Logging in to ECR...${NC}"
    aws ecr get-login-password --profile "${AWS_PROFILE}" --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
}

# Function to build and push resort scraper
build_resort_scraper() {
    echo -e "${YELLOW}Building resort scraper ECS image (linux/amd64)...${NC}"
    cd "$PROJECT_ROOT"
    
    # Build and push ECS image
    docker buildx build \
        --platform linux/amd64 \
        --push \
        -f Dockerfile.resort-scraper \
        -t "${RESORT_ECR_URL}:latest" \
        .
    
    echo -e "${GREEN}✓ Resort scraper image built and pushed${NC}"
}

# Function to build and push SNOTEL scraper
build_snotel() {
    echo -e "${YELLOW}Building SNOTEL Lambda image (linux/amd64)...${NC}"
    cd "$PROJECT_ROOT"
    
    # Build and push with provenance=false to create single-manifest image (Lambda requirement)
    docker buildx build \
        --platform linux/amd64 \
        --provenance=false \
        --push \
        -f lambdas/snotel/Dockerfile \
        -t "${SNOTEL_ECR_URL}:latest" \
        .
    
    echo -e "${GREEN}✓ SNOTEL image built and pushed${NC}"
}

# Function to build and push forecast scraper
build_forecast() {
    echo -e "${YELLOW}Building forecast Lambda image (linux/amd64)...${NC}"
    cd "$PROJECT_ROOT"
    
    # Build and push with provenance=false to create single-manifest image (Lambda requirement)
    docker buildx build \
        --platform linux/amd64 \
        --provenance=false \
        --push \
        -f lambdas/forecast/Dockerfile \
        -t "${FORECAST_ECR_URL}:latest" \
        .
    
    echo -e "${GREEN}✓ Forecast image built and pushed${NC}"
}

# Function to build and push historical weather scraper
build_historical_weather() {
    echo -e "${YELLOW}Building historical weather Lambda image (linux/amd64)...${NC}"
    cd "$PROJECT_ROOT"
    
    # Build and push with provenance=false to create single-manifest image (Lambda requirement)
    docker buildx build \
        --platform linux/amd64 \
        --provenance=false \
        --push \
        -f lambdas/historical_weather/Dockerfile \
        -t "${HISTORICAL_WEATHER_ECR_URL}:latest" \
        .
    
    echo -e "${GREEN}✓ Historical weather image built and pushed${NC}"
}

# Main logic
TARGET="${1:-all}"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Container Build and Push to ECR              ${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "AWS Profile: ${AWS_PROFILE}"
echo "AWS Account ID: ${AWS_ACCOUNT_ID}"
echo "AWS Region: ${AWS_REGION}"
echo "Target: ${TARGET}"
echo ""
echo "To use a different profile, set AWS_PROFILE:"
echo "  export AWS_PROFILE=your-profile-name"
echo "  $0 ${TARGET}"
echo ""

# Login to ECR
ecr_login

# Build and push based on target
case "$TARGET" in
    "resort-scraper")
        build_resort_scraper
        ;;
    "snotel")
        build_snotel
        ;;
    "forecast")
        build_forecast
        ;;
    "historical-weather")
        build_historical_weather
        ;;
    "all")
        build_resort_scraper
        echo ""
        build_snotel
        echo ""
        build_forecast
        echo ""
        build_historical_weather
        ;;
    *)
        echo -e "${RED}Error: Unknown target '$TARGET'${NC}"
        echo "Usage: $0 [resort-scraper|snotel|forecast|historical-weather|all]"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Build and Push Complete!                     ${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Resort Scraper: ${RESORT_ECR_URL}:latest"
echo "SNOTEL: ${SNOTEL_ECR_URL}:latest"
echo "Forecast: ${FORECAST_ECR_URL}:latest"
echo "Historical Weather: ${HISTORICAL_WEATHER_ECR_URL}:latest"
