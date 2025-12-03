#!/bin/bash
# Helper script to get EC2 instance details for database connection
# Usage: ./scripts/get-ec2-details.sh [instance-name-or-id]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

AWS_PROFILE="${AWS_PROFILE:-default}"

# Get instance identifier from argument or prompt
INSTANCE_IDENTIFIER="$1"

if [ -z "$INSTANCE_IDENTIFIER" ]; then
    echo -e "${YELLOW}No instance specified. Listing all instances...${NC}"
    echo ""
    aws ec2 describe-instances --profile "${AWS_PROFILE}" \
      --query 'Reservations[*].Instances[*].[InstanceId,Tags[?Key==`Name`].Value|[0],State.Name,PrivateIpAddress,PublicIpAddress]' \
      --output table
    
    echo ""
    read -p "Enter instance ID or Name tag: " INSTANCE_IDENTIFIER
fi

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  EC2 Instance Details                         ${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "AWS Profile: ${AWS_PROFILE}"
echo "Instance: ${INSTANCE_IDENTIFIER}"
echo ""

# Try to get instance by ID first, then by Name tag
if [[ "$INSTANCE_IDENTIFIER" =~ ^i- ]]; then
    # It's an instance ID
    INSTANCE_DATA=$(aws ec2 describe-instances --profile "${AWS_PROFILE}" \
      --instance-ids "$INSTANCE_IDENTIFIER" \
      --query 'Reservations[0].Instances[0]' \
      --output json 2>/dev/null)
else
    # It's a Name tag
    INSTANCE_DATA=$(aws ec2 describe-instances --profile "${AWS_PROFILE}" \
      --filters "Name=tag:Name,Values=${INSTANCE_IDENTIFIER}" "Name=instance-state-name,Values=running" \
      --query 'Reservations[0].Instances[0]' \
      --output json 2>/dev/null)
fi

if [ -z "$INSTANCE_DATA" ] || [ "$INSTANCE_DATA" == "null" ]; then
    echo -e "${RED}Error: Instance not found${NC}"
    exit 1
fi

# Extract values
INSTANCE_ID=$(echo "$INSTANCE_DATA" | jq -r '.InstanceId')
INSTANCE_NAME=$(echo "$INSTANCE_DATA" | jq -r '.Tags[]? | select(.Key=="Name") | .Value // "N/A"')
PRIVATE_IP=$(echo "$INSTANCE_DATA" | jq -r '.PrivateIpAddress // "N/A"')
PUBLIC_IP=$(echo "$INSTANCE_DATA" | jq -r '.PublicIpAddress // "N/A"')
PRIVATE_DNS=$(echo "$INSTANCE_DATA" | jq -r '.PrivateDnsName // "N/A"')
PUBLIC_DNS=$(echo "$INSTANCE_DATA" | jq -r '.PublicDnsName // "N/A"')
VPC_ID=$(echo "$INSTANCE_DATA" | jq -r '.VpcId // "N/A"')
SUBNET_ID=$(echo "$INSTANCE_DATA" | jq -r '.SubnetId // "N/A"')
SECURITY_GROUPS=$(echo "$INSTANCE_DATA" | jq -r '.SecurityGroups[]?.GroupId' | tr '\n' ',' | sed 's/,$//')

echo -e "${CYAN}Instance Information:${NC}"
echo "  Instance ID: ${INSTANCE_ID}"
echo "  Name: ${INSTANCE_NAME}"
echo "  VPC ID: ${VPC_ID}"
echo "  Subnet ID: ${SUBNET_ID}"
echo "  Security Groups: ${SECURITY_GROUPS}"
echo ""

echo -e "${CYAN}Network Information:${NC}"
echo "  Private IP: ${PRIVATE_IP}"
echo "  Private DNS: ${PRIVATE_DNS}"
if [ "$PUBLIC_IP" != "N/A" ]; then
    echo "  Public IP: ${PUBLIC_IP}"
    echo "  Public DNS: ${PUBLIC_DNS}"
else
    echo "  Public IP: Not assigned"
fi
echo ""

echo -e "${GREEN}Recommended DATABASE_URL (using Private IP):${NC}"
echo -e "${YELLOW}postgresql://username:password@${PRIVATE_IP}:5432/dbname${NC}"
echo ""

if [ "$PUBLIC_IP" != "N/A" ]; then
    echo -e "${YELLOW}Alternative DATABASE_URL (using Public IP - less secure):${NC}"
    echo -e "${YELLOW}postgresql://username:password@${PUBLIC_IP}:5432/dbname${NC}"
    echo ""
fi

echo -e "${CYAN}To set the secret:${NC}"
echo "aws secretsmanager create-secret --profile ${AWS_PROFILE} \\"
echo "  --name corduroy/database-url \\"
echo "  --secret-string \"postgresql://username:password@${PRIVATE_IP}:5432/dbname\""
echo ""

