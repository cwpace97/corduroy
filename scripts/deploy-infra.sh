#!/bin/bash
# Deploy infrastructure using Terraform
# Usage: ./scripts/deploy-infra.sh [plan|apply|destroy]

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
INFRA_DIR="${PROJECT_ROOT}/infrastructure"

# Terraform command
ACTION="${1:-plan}"
AWS_PROFILE="${AWS_PROFILE:-default}"

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}Error: Terraform is not installed${NC}"
    echo "Install from: https://www.terraform.io/downloads"
    exit 1
fi

# Check if terraform.tfvars exists
if [ ! -f "${INFRA_DIR}/terraform.tfvars" ]; then
    echo -e "${YELLOW}Warning: terraform.tfvars not found${NC}"
    echo "Copy terraform.tfvars.example to terraform.tfvars and configure it:"
    echo "  cp ${INFRA_DIR}/terraform.tfvars.example ${INFRA_DIR}/terraform.tfvars"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Terraform Infrastructure Deployment         ${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "AWS Profile: ${AWS_PROFILE}"
echo "Action: ${ACTION}"
echo "Directory: ${INFRA_DIR}"
echo ""
echo "To use a different profile, set AWS_PROFILE:"
echo "  export AWS_PROFILE=your-profile-name"
echo "  $0 ${ACTION}"
echo ""

cd "${INFRA_DIR}"

# Export AWS profile for Terraform
export AWS_PROFILE="${AWS_PROFILE}"

# Initialize Terraform
echo -e "${YELLOW}Initializing Terraform...${NC}"
terraform init

# Run terraform command
case "$ACTION" in
    "plan")
        echo -e "${YELLOW}Running terraform plan...${NC}"
        terraform plan
        ;;
    "apply")
        echo -e "${YELLOW}Running terraform apply...${NC}"
        terraform apply
        ;;
    "destroy")
        echo -e "${RED}Warning: This will destroy all infrastructure!${NC}"
        read -p "Are you sure? Type 'yes' to continue: " confirm
        if [ "$confirm" != "yes" ]; then
            echo "Aborted"
            exit 1
        fi
        terraform destroy
        ;;
    "validate")
        echo -e "${YELLOW}Validating Terraform configuration...${NC}"
        terraform validate
        ;;
    "fmt")
        echo -e "${YELLOW}Formatting Terraform files...${NC}"
        terraform fmt -recursive
        ;;
    *)
        echo -e "${RED}Error: Unknown action '$ACTION'${NC}"
        echo "Usage: $0 [plan|apply|destroy|validate|fmt]"
        exit 1
        ;;
esac

if [ "$ACTION" = "apply" ]; then
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}  Deployment Complete!                        ${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
    echo "Outputs:"
    terraform output
fi

