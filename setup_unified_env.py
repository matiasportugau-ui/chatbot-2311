#!/usr/bin/env python3
"""
Unified .env Setup Script
Helps create and manage .env file with all required keys and tokens
"""

import os
import sys
from pathlib import Path
from typing import Dict, List

# Color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}\n")

def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

# All required environment variables organized by category
ENV_TEMPLATE = {
    "AI_MODELS": {
        "OPENAI_API_KEY": {
            "required": True,
            "description": "OpenAI API Key (required for main AI functionality)",
            "example": "sk-...",
            "get_from": "https://platform.openai.com/api-keys"
        },
        "GROQ_API_KEY": {
            "required": False,
            "description": "Groq API Key (free tier available, great for speed)",
            "example": "gsk_...",
            "get_from": "https://console.groq.com/keys"
        },
        "GEMINI_API_KEY": {
            "required": False,
            "description": "Google Gemini API Key",
            "example": "AIza...",
            "get_from": "https://aistudio.google.com/app/apikey"
        },
        "GROK_API_KEY": {
            "required": False,
            "description": "xAI (Grok) API Key",
            "example": "xai-...",
            "get_from": "https://console.x.ai/keys"
        },
        "OPENAI_ORGANIZATION_ID": {
            "required": False,
            "description": "OpenAI Organization ID (optional)",
            "example": "org-...",
            "get_from": "OpenAI Organization Settings"
        },
        "OPENAI_PROJECT_ID": {
            "required": False,
            "description": "OpenAI Project ID (optional)",
            "example": "proj-...",
            "get_from": "OpenAI Project Settings"
        }
    },
    "DATABASES": {
        "MONGODB_URI": {
            "required": True,
            "description": "MongoDB connection string",
            "example": "mongodb://localhost:27017/bmc_chat",
            "get_from": "Local MongoDB or MongoDB Atlas"
        },
        "DATABASE_URL": {
            "required": False,
            "description": "PostgreSQL connection string (optional)",
            "example": "postgresql://user:pass@localhost:5432/bmc_dashboard",
            "get_from": "PostgreSQL database"
        }
    },
    "WHATSAPP": {
        "WHATSAPP_ACCESS_TOKEN": {
            "required": False,
            "description": "WhatsApp Business API Access Token",
            "example": "EAA...",
            "get_from": "Meta Business Developer Portal"
        },
        "WHATSAPP_VERIFY_TOKEN": {
            "required": False,
            "description": "WhatsApp Webhook Verify Token",
            "example": "your-verify-token",
            "get_from": "Create your own secure token"
        },
        "WHATSAPP_PHONE_NUMBER_ID": {
            "required": False,
            "description": "WhatsApp Business Phone Number ID",
            "example": "123456789012345",
            "get_from": "Meta Business Developer Portal"
        },
        "WHATSAPP_BUSINESS_ID": {
            "required": False,
            "description": "WhatsApp Business Account ID",
            "example": "123456789012345",
            "get_from": "Meta Business Developer Portal"
        },
        "WHATSAPP_APP_SECRET": {
            "required": False,
            "description": "WhatsApp App Secret",
            "example": "your-app-secret",
            "get_from": "Meta Business Developer Portal"
        }
    },
    "MERCADO_LIBRE": {
        "MERCADO_LIBRE_APP_ID": {
            "required": False,
            "description": "MercadoLibre Application ID",
            "example": "1234567890123456",
            "get_from": "https://developers.mercadolibre.com.uy"
        },
        "MERCADO_LIBRE_CLIENT_SECRET": {
            "required": False,
            "description": "MercadoLibre Client Secret",
            "example": "your-client-secret",
            "get_from": "https://developers.mercadolibre.com.uy"
        },
        "MELI_ACCESS_TOKEN": {
            "required": False,
            "description": "MercadoLibre Access Token",
            "example": "APP_USR-...",
            "get_from": "MercadoLibre OAuth flow"
        },
        "MELI_REFRESH_TOKEN": {
            "required": False,
            "description": "MercadoLibre Refresh Token",
            "example": "TG-...",
            "get_from": "MercadoLibre OAuth flow"
        },
        "MELI_SELLER_ID": {
            "required": False,
            "description": "MercadoLibre Seller ID",
            "example": "123456789",
            "get_from": "MercadoLibre Account"
        }
    },
    "N8N": {
        "N8N_BASIC_AUTH_PASSWORD": {
            "required": False,
            "description": "n8n Basic Auth Password",
            "example": "your-secure-password",
            "get_from": "Set in n8n configuration"
        },
        "N8N_API_KEY": {
            "required": False,
            "description": "n8n API Key",
            "example": "your-n8n-api-key",
            "get_from": "n8n Settings → API"
        }
    },
    "GOOGLE": {
        "GOOGLE_SHEETS_API_KEY": {
            "required": False,
            "description": "Google Sheets API Key",
            "example": "AIza...",
            "get_from": "Google Cloud Console"
        }
    },
    "OTHER": {
        "NEXTAUTH_SECRET": {
            "required": False,
            "description": "NextAuth.js Secret (generate random string)",
            "example": "your-random-secret-key",
            "get_from": "Generate: openssl rand -base64 32"
        },
        "SENTRY_DSN": {
            "required": False,
            "description": "Sentry DSN for error tracking",
            "example": "https://...@sentry.io/...",
            "get_from": "Sentry.io project settings"
        }
    }
}

def create_env_file(interactive: bool = True) -> Dict[str, str]:
    """Create .env file interactively or from existing values"""
    env_file = Path(".env")
    env_values = {}
    
    # Load existing .env if it exists
    if env_file.exists():
        print_info("Found existing .env file, loading current values...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_values[key.strip()] = value.strip()
        print_success(f"Loaded {len(env_values)} existing values")
    
    # Load from environment variables
    for category, vars_dict in ENV_TEMPLATE.items():
        for var_name in vars_dict.keys():
            if var_name in os.environ and var_name not in env_values:
                env_values[var_name] = os.environ[var_name]
    
    if not interactive:
        return env_values
    
    print_header("Unified .env Setup")
    print("This script will help you create a complete .env file with all required keys.\n")
    print("You can:")
    print("  - Enter values manually")
    print("  - Press Enter to skip optional variables")
    print("  - Press Enter to keep existing values\n")
    
    input("Press Enter to continue...")
    
    # Collect values interactively
    for category, vars_dict in ENV_TEMPLATE.items():
        print(f"\n{Colors.BOLD}{Colors.OKCYAN}━━━ {category} ━━━{Colors.ENDC}")
        
        for var_name, var_info in vars_dict.items():
            required = var_info["required"]
            description = var_info["description"]
            example = var_info["example"]
            get_from = var_info["get_from"]
            
            # Show current value if exists
            current_value = env_values.get(var_name, "")
            if current_value:
                display_value = current_value[:20] + "..." if len(current_value) > 20 else current_value
                prompt = f"{var_name} [{Colors.OKGREEN}current: {display_value}{Colors.ENDC}]"
            else:
                prompt = var_name
                if required:
                    prompt += f" {Colors.FAIL}[REQUIRED]{Colors.ENDC}"
            
            print(f"\n{Colors.OKBLUE}{var_name}{Colors.ENDC}")
            print(f"  {description}")
            print(f"  Example: {example}")
            print(f"  Get from: {get_from}")
            
            if current_value and not required:
                user_input = input(f"\n{prompt} (Enter to keep, 'skip' to remove): ").strip()
                if user_input.lower() == 'skip':
                    env_values.pop(var_name, None)
                    continue
                elif not user_input:
                    continue
            else:
                user_input = input(f"\n{prompt}: ").strip()
            
            if user_input:
                env_values[var_name] = user_input
            elif required and not current_value:
                print_warning(f"{var_name} is required but not provided")
    
    return env_values

def write_env_file(env_values: Dict[str, str], output_file: str = ".env"):
    """Write .env file with organized structure"""
    env_file = Path(output_file)
    
    # Create backup if exists
    if env_file.exists():
        backup_file = env_file.with_suffix('.env.backup')
        import shutil
        shutil.copy(env_file, backup_file)
        print_info(f"Created backup: {backup_file}")
    
    # Write organized .env file
    with open(env_file, 'w') as f:
        f.write("# ============================================\n")
        f.write("# BMC Chatbot - Unified Environment Variables\n")
        f.write("# ============================================\n")
        f.write("# Generated by setup_unified_env.py\n")
        f.write("# DO NOT COMMIT THIS FILE TO GIT!\n\n")
        
        for category, vars_dict in ENV_TEMPLATE.items():
            f.write(f"\n# ============================================\n")
            f.write(f"# {category}\n")
            f.write(f"# ============================================\n\n")
            
            for var_name, var_info in vars_dict.items():
                value = env_values.get(var_name, "")
                
                if value:
                    f.write(f"# {var_info['description']}\n")
                    f.write(f"# Get from: {var_info['get_from']}\n")
                    f.write(f"{var_name}={value}\n\n")
                else:
                    required = "REQUIRED" if var_info["required"] else "OPTIONAL"
                    f.write(f"# {var_info['description']} [{required}]\n")
                    f.write(f"# Get from: {var_info['get_from']}\n")
                    f.write(f"# {var_name}={var_info['example']}\n\n")
        
        # Add other common variables
        f.write("\n# ============================================\n")
        f.write("# Configuration\n")
        f.write("# ============================================\n\n")
        f.write("MODEL_STRATEGY=balanced\n")
        f.write("LOG_LEVEL=INFO\n")
        f.write("ENABLE_REQUEST_TRACKING=true\n")
        f.write("NEXT_PUBLIC_ENABLE_AI_INSIGHTS=true\n")
        f.write("NEXT_PUBLIC_ENABLE_REAL_TIME_MONITORING=true\n")
        f.write("NEXT_PUBLIC_ENABLE_EXPORT_IMPORT=true\n")
    
    print_success(f"Created .env file: {env_file}")
    print_info(f"Total variables: {len([v for v in env_values.values() if v])}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup unified .env file")
    parser.add_argument("--non-interactive", action="store_true", 
                       help="Create .env from existing environment variables only")
    parser.add_argument("--output", default=".env", 
                       help="Output file name (default: .env)")
    
    args = parser.parse_args()
    
    try:
        env_values = create_env_file(interactive=not args.non_interactive)
        write_env_file(env_values, args.output)
        
        print_header("Setup Complete!")
        print_success(".env file created successfully")
        print("\nNext steps:")
        print("  1. Review the .env file: cat .env")
        print("  2. Upload to GitHub Codespaces: python upload_secrets_to_github.py")
        print("  3. Or use manually in Codespaces\n")
        
    except KeyboardInterrupt:
        print_error("\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

