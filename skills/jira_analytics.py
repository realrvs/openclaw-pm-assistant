import os
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta

# Загружаем настройки из .env
try:
    from dotenv import load_dotenv
    load_dotenv(Path.home() / '.openclaw/workspace/skills/jira/.env')
except ImportError:
    pass

class JiraClient:
    def __init__(self):
        self.url = os.getenv('JIRA_URL')
        self.email = os.getenv('JIRA_EMAIL')
        self.token = os.getenv('JIRA_TOKEN')
        self.auth = (self.email, self.token)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_projects(self):
        """Получить список всех проектов"""
        response = requests.get(
            f'{self.url}/rest/api/2/project',
            auth=self.auth,
            headers=self.headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Ошибка получения проектов: {response.status_code}")
            return []

    def get_issues(self, project_key, days=365):
        """Получить задачи по проекту за последние N дней"""
        jql = f'project={project_key} AND updated >= -{days}d'
        response = requests.get(
            f'{self.url}/rest/api/2/search',
            params={'jql': jql, 'maxResults': 100},
            auth=self.auth,
            headers=self.headers
        )
        if response.status_code == 200:
            return response.json().get('issues', [])
        else:
            print(f"❌ Ошибка Jira: {response.status_code}")
            return []

    def get_blocked_issues(self, project_key):
        """Получить заблокированные задачи"""
        jql = f'project={project_key} AND status="Blocked"'
        response = requests.get(
            f'{self.url}/rest/api/2/search',
            params={'jql': jql},
            auth=self.auth,
            headers=self.headers
        )
        if response.status_code == 200:
            return response.json().get('issues', [])
        return []

    def get_project_summary(self, project_key, days=365):
        """Получить сводку по проекту"""
        issues = self.get_issues(project_key, days)
        blocked = self.get_blocked_issues(project_key)

        summary = {
            'total': len(issues),
            'blocked': len(blocked),
            'in_progress': 0,
            'done': 0,
            'statuses': {}
        }

        # Список статусов, которые считаются завершёнными
        done_statuses = ['done', 'closed', 'resolved', 'completed', 'закрыт', 'выполнено']

        for issue in issues:
            status = issue['fields']['status']['name'].lower()
            summary['statuses'][status] = summary['statuses'].get(status, 0) + 1
            
            if status in ['in progress', 'in review', 'in development', 'в работе', 'в процессе']:
                summary['in_progress'] += 1
            elif status in done_statuses:
                summary['done'] += 1

        return summary

if __name__ == "__main__":
    # Тест клиента
    client = JiraClient()
    print("✅ Jira клиент инициализирован")
    print(f"🔗 URL: {client.url}")
    print(f"📧 Email: {client.email}")
    print(f"🔑 Token: {client.token[:10]}..." if client.token else "❌ Токен не задан")
