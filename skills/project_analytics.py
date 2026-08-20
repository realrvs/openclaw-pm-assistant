import json
from pathlib import Path
from jira_analytics import JiraClient

PROJECTS_FILE = Path.home() / '.openclaw/workspace/data/projects.json'

def load_projects():
    with open(PROJECTS_FILE) as f:
        return json.load(f)['projects']

def get_status():
    jira = JiraClient()
    projects = load_projects()
    output = "📊 **Статус проектов (с Jira):**\n\n"
    
    for p in projects:
        # Пробуем получить данные из Jira по ключу проекта
        summary = jira.get_project_summary(p['id'], days=365)
        
        output += f"**{p['name']}**\n"
        output += f"  - Статус: {p['status']}\n"
        output += f"  - Команда: {p['team_size']} чел.\n"
        output += f"  - Технологии: {', '.join(p['tech_stack'])}\n"
        output += f"  - Риски: {', '.join(p['risks'])}\n"
        output += f"  - 📋 Всего задач (Jira): {summary['total']}\n"
        output += f"  - 🔄 В работе: {summary['in_progress']}\n"
        output += f"  - 🚫 Заблокировано: {summary['blocked']}\n"
        output += f"  - ✅ Завершено: {summary['done']}\n\n"
    
    return output

def get_risks():
    projects = load_projects()
    output = "⚠️ **Актуальные риски:**\n\n"
    for p in projects:
        if p['risks']:
            output += f"**{p['name']}**:\n"
            for risk in p['risks']:
                output += f"  - {risk}\n"
    return output

def get_project_details(project_id):
    projects = load_projects()
    for p in projects:
        if p['id'].lower() == project_id.lower():
            output = f"📁 **Детали проекта: {p['name']}**\n\n"
            output += f"- Статус: {p['status']}\n"
            output += f"- Команда: {p['team_size']} чел.\n"
            output += f"- Технологии: {', '.join(p['tech_stack'])}\n"
            output += f"- Риски: {', '.join(p['risks'])}\n"
            output += f"- Обновлено: {p['last_update']}\n"
            return output
    return f"❌ Проект с ID '{project_id}' не найден."

if __name__ == "__main__":
    print("=== СТАТУС ПРОЕКТОВ (с Jira) ===")
    print(get_status())
    print("\n=== РИСКИ ===")
    print(get_risks())
