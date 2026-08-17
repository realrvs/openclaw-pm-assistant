#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime
from pathlib import Path

REPORT_PATH = Path.home() / '.openclaw/workspace/reports/data/report_data.json'
LOG_PATH = Path.home() / '.openclaw/workspace/reports/logs/collector.log'

def log_message(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_PATH, 'a') as f:
        f.write(f'[{timestamp}] {msg}\n')
    print(f'[{timestamp}] {msg}')

def collect_metrics():
    # Тестовые данные (в реальном проекте — запрос к Jira API)
    data = {
        "timestamp": datetime.now().isoformat(),
        "projects": [
            {
                "id": "RUS",
                "name": "Автоматизация закупок РусГидро",
                "total_tasks": 42,
                "blocked": 3,
                "in_progress": 12,
                "completed_last_week": 8
            },
            {
                "id": "DIT",
                "name": "Магазин приложений для МЭШ",
                "total_tasks": 28,
                "blocked": 0,
                "in_progress": 8,
                "completed_last_week": 15
            },
            {
                "id": "VTB",
                "name": "Модернизация систем ВТБ",
                "total_tasks": 156,
                "blocked": 7,
                "in_progress": 34,
                "completed_last_week": 22
            }
        ],
        "summary": {
            "total_tasks": 226,
            "total_blocked": 10,
            "total_in_progress": 54,
            "total_completed": 45
        }
    }
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    log_message(f"✅ Данные сохранены: {REPORT_PATH}")
    return data

def generate_fallback_report(data):
    report = f"📊 **Ежедневный отчёт (без AI)**\n"
    report += f"Дата: {datetime.now().strftime('%d.%m.%Y')}\n\n"
    
    report += "### 📋 Сводка\n"
    report += f"- Всего задач: {data['summary']['total_tasks']}\n"
    report += f"- В работе: {data['summary']['total_in_progress']}\n"
    report += f"- Заблокировано: {data['summary']['total_blocked']}\n"
    report += f"- Завершено за неделю: {data['summary']['total_completed']}\n\n"
    
    report += "### 📁 Проекты\n"
    for p in data['projects']:
        report += f"**{p['name']}**\n"
        report += f"  - Всего задач: {p['total_tasks']}\n"
        report += f"  - В работе: {p['in_progress']}\n"
        report += f"  - Заблокировано: {p['blocked']}\n"
        report += f"  - Завершено за неделю: {p['completed_last_week']}\n\n"
    
    report += "⚠️ *Отчёт сгенерирован в резервном режиме (LLM недоступен)*"
    return report

if __name__ == "__main__":
    try:
        log_message("🚀 Запуск сбора данных...")
        data = collect_metrics()
        
        if len(sys.argv) > 1 and sys.argv[1] == "--fallback":
            report = generate_fallback_report(data)
            with open(Path.home() / '.openclaw/workspace/reports/data/fallback_report.md', 'w') as f:
                f.write(report)
            log_message("✅ Сгенерирован резервный отчёт")
        
        log_message("✅ Скрипт завершён успешно")
    except Exception as e:
        log_message(f"❌ Ошибка: {e}")
        sys.exit(1)
