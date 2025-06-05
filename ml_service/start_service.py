#!/usr/bin/env python3
"""
🚀 Скрипт запуску Music Recommender ML Service
"""

import subprocess
import sys
import os
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_python():
    """Перевірка версії Python"""
    if sys.version_info < (3, 8):
        logger.error("❌ Потрібен Python 3.8 або новіший")
        sys.exit(1)
    logger.info(f"✅ Python {sys.version}")

def install_requirements():
    """Встановлення залежностей"""
    try:
        logger.info("📦 Встановлення залежностей...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("✅ Залежності встановлено")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Помилка встановлення залежностей: {e}")
        sys.exit(1)

def start_service():
    """Запуск ML сервісу"""
    try:
        logger.info("🚀 Запуск Music Recommender ML Service...")
        logger.info("🌐 Сервіс буде доступний на http://localhost:8000")
        logger.info("📚 API документація: http://localhost:8000/docs")
        logger.info("🔄 Для зупинки натисніть Ctrl+C")
        
        # Запуск uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        logger.info("🛑 Сервіс зупинено користувачем")
    except Exception as e:
        logger.error(f"❌ Помилка запуску сервісу: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🎵 Music Recommender ML Service 2.0")
    print("=" * 50)
    
    check_python()
    
    # Перевіряємо чи існує requirements.txt
    if os.path.exists("requirements.txt"):
        install_requirements()
    else:
        logger.warning("⚠️ requirements.txt не знайдено, пропускаємо встановлення залежностей")
    
    start_service() 