import json
import sys
from pathlib import Path
from jira_analytics import JiraClient

PROJECTS_FILE = Path.home() / '.openclaw/workspace/data/projects.json'

def load_projects():
    with open(PROJECTS_FILE) as f:
        return json.load(f)['projects']

def get_detailed_jira_data():
    """Собирает детальные данные из Jira"""
    jira = JiraClient()
    projects = load_projects()
    
    all_data = []
    
    for p in projects:
        summary = jira.get_project_summary(p['id'], days=365)
        
        project_data = {
            "project": {
                "id": p['id'],
                "name": p['name'],
                "status": p['status']
            },
            "summary": {
                "total_issues": summary['total'],
                "in_progress": summary['in_progress'],
                "blocked": summary['blocked'],
                "done": summary['done']
            },
            "issues": []
        }
        
        # Форматируем задачи для LLM
        for issue in summary['issues']:
            project_data['issues'].append(jira.format_issue_for_analysis(issue))
        
        all_data.append(project_data)
    
    return all_data

def generate_analysis_prompt():
    """Генерирует промпт для LLM на основе данных Jira"""
    data = get_detailed_jira_data()
    
    prompt = """Ты — опытный руководитель проектов и аналитик. Проанализируй данные из Jira по каждому проекту.

Для каждого проекта дай:
1. Общую оценку состояния проекта (кратко)
2. Выявленные проблемы и риски
3. Рекомендации по улучшению

Особое внимание удели:
- Задачам с высоким приоритетом
- Задачам, которые долго не завершаются
- Заблокированным задачам
- Перегрузке исполнителей
- Расхождению плановой и фактической трудоёмкости

Данные по проектам:

"""
    
    for project in data:
        prompt += f"\n--- {project['project']['name']} (ID: {project['project']['id']}) ---\n"
        prompt += f"Статус проекта: {project['project']['status']}\n"
        prompt += f"Всего задач: {project['summary']['total_issues']}\n"
        prompt += f"  - В работе: {project['summary']['in_progress']}\n"
        prompt += f"  - Заблокировано: {project['summary']['blocked']}\n"
        prompt += f"  - Завершено: {project['summary']['done']}\n"
        
        if project['issues']:
            prompt += "\nЗадачи:\n"
            prompt += "\n".join(project['issues'])
        else:
            prompt += "\nНет задач за указанный период.\n"
    
    prompt += "\n\nСделай подробный аналитический вывод по каждому проекту и дай общие рекомендации для команды."
    
    return prompt

if __name__ == "__main__":
    print("=== ПРОМПТ ДЛЯ АНАЛИЗА ===\n")
    print(generate_analysis_prompt())
