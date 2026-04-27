#!/bin/bash

###############################################################################
# سكريبت تثبيت أدوات OSINT تلقائياً
# الاستخدام: sudo bash scripts/install_osint_tools.sh
###############################################################################

set -e  # إيقاف عند أي خطأ

# الألوان
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# المتغيرات
TOOLS_DIR="/opt/osint-tools"
LOG_FILE="/var/log/osint-tools-install.log"

# دالة للطباعة الملونة
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1" | tee -a "$LOG_FILE"
}

# التحقق من صلاحيات root
if [[ $EUID -ne 0 ]]; then
   print_error "يجب تشغيل هذا السكريبت بصلاحيات root"
   echo "استخدم: sudo bash $0"
   exit 1
fi

print_info "بدء تثبيت أدوات OSINT..."
echo "تاريخ التثبيت: $(date)" > "$LOG_FILE"

# إنشاء مجلد الأدوات
print_info "إنشاء مجلد الأدوات: $TOOLS_DIR"
mkdir -p "$TOOLS_DIR"
cd "$TOOLS_DIR"

###############################################################################
# 1. تحديث النظام وتثبيت المتطلبات الأساسية
###############################################################################
print_info "تحديث النظام وتثبيت المتطلبات..."

apt-get update -qq
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    golang-go \
    build-essential \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libimage-exiftool-perl \
    jq \
    >> "$LOG_FILE" 2>&1

print_success "تم تثبيت المتطلبات الأساسية"

###############################################################################
# 2. تثبيت أدوات Python
###############################################################################
print_info "تثبيت أدوات Python..."

# Holehe
print_info "تثبيت Holehe..."
pip3 install holehe >> "$LOG_FILE" 2>&1 && print_success "Holehe" || print_warning "فشل تثبيت Holehe"

# Mosint
print_info "تثبيت Mosint..."
pip3 install mosint >> "$LOG_FILE" 2>&1 && print_success "Mosint" || print_warning "فشل تثبيت Mosint"

# h8mail
print_info "تثبيت h8mail..."
pip3 install h8mail >> "$LOG_FILE" 2>&1 && print_success "h8mail" || print_warning "فشل تثبيت h8mail"

# Twint
print_info "تثبيت Twint..."
pip3 install --upgrade -e git+https://github.com/twintproject/twint.git@origin/master#egg=twint >> "$LOG_FILE" 2>&1 && print_success "Twint" || print_warning "فشل تثبيت Twint"

# Instaloader
print_info "تثبيت Instaloader..."
pip3 install instaloader >> "$LOG_FILE" 2>&1 && print_success "Instaloader" || print_warning "فشل تثبيت Instaloader"

# Recon-ng
print_info "تثبيت Recon-ng..."
pip3 install recon-ng >> "$LOG_FILE" 2>&1 && print_success "Recon-ng" || print_warning "فشل تثبيت Recon-ng"

# Shodan
print_info "تثبيت Shodan CLI..."
pip3 install shodan >> "$LOG_FILE" 2>&1 && print_success "Shodan" || print_warning "فشل تثبيت Shodan"

###############################################################################
# 3. تثبيت أدوات من GitHub
###############################################################################
print_info "تثبيت أدوات من GitHub..."

# Sublist3r
print_info "تثبيت Sublist3r..."
if [ ! -d "Sublist3r" ]; then
    git clone https://github.com/aboul3la/Sublist3r.git >> "$LOG_FILE" 2>&1
    cd Sublist3r
    pip3 install -r requirements.txt >> "$LOG_FILE" 2>&1
    cd ..
    print_success "Sublist3r"
else
    print_warning "Sublist3r موجود مسبقاً"
fi

# theHarvester
print_info "تثبيت theHarvester..."
if [ ! -d "theHarvester" ]; then
    git clone https://github.com/laramies/theHarvester.git >> "$LOG_FILE" 2>&1
    cd theHarvester
    pip3 install -r requirements.txt >> "$LOG_FILE" 2>&1
    cd ..
    print_success "theHarvester"
else
    print_warning "theHarvester موجود مسبقاً"
fi

# Sherlock
print_info "تثبيت Sherlock..."
if [ ! -d "sherlock" ]; then
    git clone https://github.com/sherlock-project/sherlock.git >> "$LOG_FILE" 2>&1
    cd sherlock
    pip3 install -r requirements.txt >> "$LOG_FILE" 2>&1
    cd ..
    print_success "Sherlock"
else
    print_warning "Sherlock موجود مسبقاً"
fi

# Maigret
print_info "تثبيت Maigret..."
if [ ! -d "maigret" ]; then
    git clone https://github.com/soxoj/maigret.git >> "$LOG_FILE" 2>&1
    cd maigret
    pip3 install -r requirements.txt >> "$LOG_FILE" 2>&1
    cd ..
    print_success "Maigret"
else
    print_warning "Maigret موجود مسبقاً"
fi

# Blackbird
print_info "تثبيت Blackbird..."
if [ ! -d "blackbird" ]; then
    git clone https://github.com/p1ngul1n0/blackbird.git >> "$LOG_FILE" 2>&1
    cd blackbird
    pip3 install -r requirements.txt >> "$LOG_FILE" 2>&1
    cd ..
    print_success "Blackbird"
else
    print_warning "Blackbird موجود مسبقاً"
fi

# Nexfil
print_info "تثبيت Nexfil..."
if [ ! -d "nexfil" ]; then
    git clone https://github.com/thewhiteh4t/nexfil.git >> "$LOG_FILE" 2>&1
    cd nexfil
    pip3 install -r requirements.txt >> "$LOG_FILE" 2>&1
    cd ..
    print_success "Nexfil"
else
    print_warning "Nexfil موجود مسبقاً"
fi

# Snoop
print_info "تثبيت Snoop..."
if [ ! -d "snoop" ]; then
    git clone https://github.com/snooppr/snoop.git >> "$LOG_FILE" 2>&1
    cd snoop
    pip3 install -r requirements.txt >> "$LOG_FILE" 2>&1
    cd ..
    print_success "Snoop"
else
    print_warning "Snoop موجود مسبقاً"
fi

# Social-Analyzer
print_info "تثبيت Social-Analyzer..."
if [ ! -d "social-analyzer" ]; then
    git clone https://github.com/qeeqbox/social-analyzer.git >> "$LOG_FILE" 2>&1
    cd social-analyzer
    pip3 install -r requirements.txt >> "$LOG_FILE" 2>&1
    cd ..
    print_success "Social-Analyzer"
else
    print_warning "Social-Analyzer موجود مسبقاً"
fi

# PhoneInfoga
print_info "تثبيت PhoneInfoga..."
if [ ! -d "phoneinfoga" ]; then
    git clone https://github.com/sundowndev/phoneinfoga.git >> "$LOG_FILE" 2>&1
    cd phoneinfoga
    if command -v go &> /dev/null; then
        go build >> "$LOG_FILE" 2>&1
        print_success "PhoneInfoga"
    else
        print_warning "Go غير مثبت، تخطي PhoneInfoga"
    fi
    cd ..
else
    print_warning "PhoneInfoga موجود مسبقاً"
fi

# Metagoofil
print_info "تثبيت Metagoofil..."
if [ ! -d "metagoofil" ]; then
    git clone https://github.com/laramies/metagoofil.git >> "$LOG_FILE" 2>&1
    cd metagoofil
    pip3 install -r requirements.txt >> "$LOG_FILE" 2>&1
    cd ..
    print_success "Metagoofil"
else
    print_warning "Metagoofil موجود مسبقاً"
fi

# DNSRecon
print_info "تثبيت DNSRecon..."
if [ ! -d "dnsrecon" ]; then
    git clone https://github.com/darkoperator/dnsrecon.git >> "$LOG_FILE" 2>&1
    cd dnsrecon
    pip3 install -r requirements.txt >> "$LOG_FILE" 2>&1
    cd ..
    print_success "DNSRecon"
else
    print_warning "DNSRecon موجود مسبقاً"
fi

###############################################################################
# 4. تثبيت أدوات Go
###############################################################################
print_info "تثبيت أدوات Go..."

if command -v go &> /dev/null; then
    export GOPATH=$HOME/go
    export PATH=$PATH:$GOPATH/bin
    
    # Amass
    print_info "تثبيت Amass..."
    go install -v github.com/OWASP/Amass/v3/...@master >> "$LOG_FILE" 2>&1 && print_success "Amass" || print_warning "فشل تثبيت Amass"
    
    # Subfinder
    print_info "تثبيت Subfinder..."
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest >> "$LOG_FILE" 2>&1 && print_success "Subfinder" || print_warning "فشل تثبيت Subfinder"
    
    # Assetfinder
    print_info "تثبيت Assetfinder..."
    go install github.com/tomnomnom/assetfinder@latest >> "$LOG_FILE" 2>&1 && print_success "Assetfinder" || print_warning "فشل تثبيت Assetfinder"
    
    # Httprobe
    print_info "تثبيت Httprobe..."
    go install github.com/tomnomnom/httprobe@latest >> "$LOG_FILE" 2>&1 && print_success "Httprobe" || print_warning "فشل تثبيت Httprobe"
else
    print_warning "Go غير مثبت، تخطي أدوات Go"
fi

###############################################################################
# 5. تثبيت أدوات من APT
###############################################################################
print_info "تثبيت أدوات من APT..."

# WhatWeb
print_info "تثبيت WhatWeb..."
apt-get install -y whatweb >> "$LOG_FILE" 2>&1 && print_success "WhatWeb" || print_warning "فشل تثبيت WhatWeb"

# ExifTool (مثبت مسبقاً)
print_success "ExifTool (مثبت مسبقاً)"

###############################################################################
# 6. إعداد الصلاحيات
###############################################################################
print_info "إعداد الصلاحيات..."
chmod -R 755 "$TOOLS_DIR"
print_success "تم إعداد الصلاحيات"

###############################################################################
# 7. إنشاء ملف تكوين
###############################################################################
print_info "إنشاء ملف التكوين..."

cat > "$TOOLS_DIR/tools_config.json" << 'EOF'
{
  "tools_directory": "/opt/osint-tools",
  "installed_tools": [
    "sherlock",
    "maigret",
    "theHarvester",
    "sublist3r",
    "blackbird",
    "nexfil",
    "snoop",
    "holehe",
    "mosint",
    "h8mail",
    "social-analyzer",
    "phoneinfoga",
    "recon-ng",
    "twint",
    "instaloader",
    "metagoofil",
    "dnsrecon",
    "whatweb",
    "exiftool",
    "shodan",
    "amass",
    "subfinder",
    "assetfinder",
    "httprobe"
  ],
  "installation_date": "$(date -I)",
  "version": "1.0"
}
EOF

print_success "تم إنشاء ملف التكوين"

###############################################################################
# 8. ملخص التثبيت
###############################################################################
echo ""
echo "=========================================="
print_success "اكتمل تثبيت أدوات OSINT!"
echo "=========================================="
echo ""
print_info "مجلد الأدوات: $TOOLS_DIR"
print_info "ملف السجل: $LOG_FILE"
echo ""
print_info "الأدوات المثبتة:"
echo "  - Sherlock, Maigret, Blackbird, Nexfil, Snoop"
echo "  - theHarvester, Sublist3r, DNSRecon, WhatWeb"
echo "  - Holehe, Mosint, h8mail"
echo "  - Social-Analyzer, Twint, Instaloader"
echo "  - PhoneInfoga, Recon-ng, Metagoofil"
echo "  - Amass, Subfinder, Assetfinder, Httprobe"
echo "  - ExifTool, Shodan CLI"
echo ""
print_info "الخطوات التالية:"
echo "  1. تشغيل: python manage.py bulk_add_tools osint_tools_data.json"
echo "  2. تكوين API keys في ملف .env"
echo "  3. اختبار الأدوات من لوحة التحكم"
echo ""
print_warning "ملاحظة: بعض الأدوات قد تحتاج تكوين إضافي"
echo "=========================================="
