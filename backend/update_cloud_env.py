#!/usr/bin/env python3
"""
Cloud Run Environment Variables Update Script

This script reads environment variables from a local .env file
and updates the Cloud Run service with those variables.

Usage:
    python update_cloud_env.py [--service nomad-backend] [--region europe-west1] [--env-file .env]
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Default values
DEFAULT_SERVICE = "nomad-backend"
DEFAULT_REGION = "europe-west1"
DEFAULT_ENV_FILE = ".env"

# Required environment variables (must be present)
REQUIRED_VARS = [
    "DB_HOST",
    "DB_PASSWORD",
    "GEMINI_API_KEY"
]

# Optional environment variables (will be added if present)
OPTIONAL_VARS = [
    "DB_USER",
    "DB_NAME",
    "DB_URL",
    "GOOGLE_REFRESH_TOKEN",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_CREDENTIALS_JSON_B64",
    "GOOGLE_CREDENTIALS_JSON"
]

def load_env_file(env_file_path):
    """Load environment variables from .env file"""
    env_path = Path(env_file_path)
    if not env_path.exists():
        print(f"❌ Error: .env file not found at {env_path.absolute()}")
        sys.exit(1)
    
    load_dotenv(dotenv_path=env_path)
    print(f"✅ Loaded .env file from {env_path.absolute()}")
    return env_path

def check_required_vars():
    """Check if all required environment variables are present"""
    missing = []
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing)}")
        print(f"   Please add them to your .env file")
        sys.exit(1)
    
    print(f"✅ All required environment variables found")

def build_env_vars_dict():
    """Build dictionary of all environment variables to set"""
    env_vars = {}
    
    # Add required vars
    for var in REQUIRED_VARS:
        value = os.getenv(var)
        if value:
            env_vars[var] = value
    
    # Add optional vars (if present)
    for var in OPTIONAL_VARS:
        value = os.getenv(var)
        if value:
            env_vars[var] = value
    
    return env_vars

def format_env_vars_for_gcloud(env_vars):
    """Format environment variables for gcloud command"""
    # Format: KEY1=value1,KEY2=value2,...
    # Special characters in values need to be handled carefully
    formatted = []
    for key, value in env_vars.items():
        # Escape special characters and wrap in quotes if needed
        # For values with special chars, use single quotes
        if any(char in value for char in [' ', '&', '|', ';', '(', ')', '$', '`']):
            # Use single quotes and escape single quotes inside
            escaped_value = value.replace("'", "'\"'\"'")
            formatted.append(f"{key}='{escaped_value}'")
        else:
            formatted.append(f"{key}={value}")
    
    return ",".join(formatted)

def update_cloud_run_env(service, region, env_vars):
    """Update Cloud Run service environment variables"""
    print(f"\n📦 Updating Cloud Run service: {service}")
    print(f"   Region: {region}")
    print(f"   Environment variables to set: {len(env_vars)}")
    
    # Build gcloud command
    env_vars_str = format_env_vars_for_gcloud(env_vars)
    
    cmd = [
        "gcloud", "run", "services", "update", service,
        "--set-env-vars", env_vars_str,
        "--region", region
    ]
    
    print(f"\n🔧 Running command:")
    print(f"   {' '.join(cmd[:6])} [ENV_VARS] --region {region}")
    print(f"\n   Environment variables:")
    for key in sorted(env_vars.keys()):
        value_preview = env_vars[key][:20] + "..." if len(env_vars[key]) > 20 else env_vars[key]
        print(f"   • {key}={value_preview}")
    
    # Ask for confirmation
    response = input(f"\n❓ Proceed with update? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ Update cancelled")
        return False
    
    # Execute command
    try:
        print(f"\n⏳ Updating Cloud Run service...")
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Successfully updated Cloud Run service!")
        print(f"\n📋 Output:")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error updating Cloud Run service:")
        print(f"   {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ Error: gcloud CLI not found")
        print(f"   Please install Google Cloud SDK: https://cloud.google.com/sdk/docs/install")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Update Cloud Run environment variables from .env file"
    )
    parser.add_argument(
        "--service",
        default=DEFAULT_SERVICE,
        help=f"Cloud Run service name (default: {DEFAULT_SERVICE})"
    )
    parser.add_argument(
        "--region",
        default=DEFAULT_REGION,
        help=f"Cloud Run region (default: {DEFAULT_REGION})"
    )
    parser.add_argument(
        "--env-file",
        default=DEFAULT_ENV_FILE,
        help=f"Path to .env file (default: {DEFAULT_ENV_FILE})"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("CLOUD RUN ENVIRONMENT VARIABLES UPDATE")
    print("=" * 60)
    
    # Load .env file
    env_path = load_env_file(args.env_file)
    
    # Check required variables
    check_required_vars()
    
    # Build environment variables dictionary
    env_vars = build_env_vars_dict()
    
    print(f"\n📋 Found {len(env_vars)} environment variables:")
    for key in sorted(env_vars.keys()):
        value_preview = env_vars[key][:30] + "..." if len(env_vars[key]) > 30 else env_vars[key]
        print(f"   • {key}: {value_preview}")
    
    # Update Cloud Run
    success = update_cloud_run_env(args.service, args.region, env_vars)
    
    if success:
        print(f"\n✅ Done! Cloud Run service updated successfully")
        print(f"\n💡 Tip: Check your service logs to verify it's working:")
        print(f"   gcloud run services logs read {args.service} --region {args.region}")
    else:
        print(f"\n❌ Failed to update Cloud Run service")
        sys.exit(1)

if __name__ == "__main__":
    main()

