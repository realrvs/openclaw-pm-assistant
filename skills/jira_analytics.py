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

def safe_get(obj, path, default=''):
    """Безопасное получение значения из вложенного словаря"""
    for key in path.split('.'):
        if obj is None:
            return default
        if isinstance(obj, dict):
            obj = obj.get(key)
        else:
            return default
    return obj if obj is not None else default

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

    def get_issues(self, project_key, days=365, fields=None):
        """Получить задачи по проекту за последние N дней"""
        jql = f'project={project_key} AND updated >= -{days}d'
        
        if fields is None:
            fields = [
                'key', 'summary', 'status', 'priority', 'assignee',
                'created', 'updated', 'timeoriginalestimate', 'timespent',
                'issuelinks', 'description', 'components', 'versions',
                'issuetype', 'reporter', 'resolution', 'resolutiondate'
            ]
        
        params = {
            'jql': jql,
            'maxResults': 100,
            'fields': ','.join(fields)
        }
        
        response = requests.get(
            f'{self.url}/rest/api/2/search',
            params=params,
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
        """Получить сводку по проекту с деталями задач"""
        issues = self.get_issues(project_key, days)
        blocked = self.get_blocked_issues(project_key)

        summary = {
            'total': len(issues),
            'blocked': len(blocked),
            'in_progress': 0,
            'done': 0,
            'statuses': {},
            'issues': []
        }

        done_statuses = ['done', 'closed', 'resolved', 'completed', 'закрыт', 'выполнено']

        for issue in issues:
            fields = issue.get('fields', {})
            status = safe_get(fields, 'status.name', '').lower()
            summary['statuses'][status] = summary['statuses'].get(status, 0) + 1
            
            if status in ['in progress', 'in review', 'in development', 'в работе', 'в процессе']:
                summary['in_progress'] += 1
            elif status in done_statuses:
                summary['done'] += 1
            
            issue_data = {
                'key': issue.get('key', ''),
                'summary': fields.get('summary', ''),
                'status': safe_get(fields, 'status.name', ''),
                'priority': safe_get(fields, 'priority.name', 'Нет'),
                'assignee': safe_get(fields, 'assignee.displayName', 'Не назначен'),
                'created': fields.get('created', ''),
                'updated': fields.get('updated', ''),
                'timeoriginalestimate': fields.get('timeoriginalestimate', 0),
                'timespent': fields.get('timespent', 0),
                'issuelinks': fields.get('issuelinks', []),
                'description': fields.get('description', ''),
                'issuetype': safe_get(fields, 'issuetype.name', ''),
                'reporter': safe_get(fields, 'reporter.displayName', ''),
                'resolution': safe_get(fields, 'resolution.name', 'Не решена'),
                'resolutiondate': fields.get('resolutiondate', '')
            }
            summary['issues'].append(issue_data)

        return summary

    def format_issue_for_analysis(self, issue_data):
        """Форматирует задачу для передачи в LLM"""
        lines = []
        lines.append(f"    - {issue_data['key']}: {issue_data['summary']}")
        lines.append(f"      Статус: {issue_data['status']}")
        lines.append(f"      Приоритет: {issue_data['priority']}")
        lines.append(f"      Исполнитель: {issue_data['assignee']}")
        lines.append(f"      Создана: {issue_data['created'][:10] if issue_data['created'] else 'Не указано'}")
        
        if issue_data['timeoriginalestimate']:
            hours = issue_data['timeoriginalestimate'] / 3600
            lines.append(f"      Плановая трудоёмкость: {hours:.1f} ч")
        else:
            lines.append(f"      Плановая трудоёмкость: Не оценено")
        
        if issue_data['timespent']:
            hours = issue_data['timespent'] / 3600
            lines.append(f"      Фактическая трудоёмкость: {hours:.1f} ч")
        else:
            lines.append(f"      Фактическая трудоёмкость: Не указано")
        
        if issue_data['issuelinks']:
            links = []
            for link in issue_data['issuelinks']:
                if 'outwardIssue' in link:
                    links.append(f"{link.get('type', {}).get('name', 'связана')} -> {link['outwardIssue']['key']}")
                elif 'inwardIssue' in link:
                    links.append(f"{link['inwardIssue']['key']} -> {link.get('type', {}).get('name', 'связана')}")
            if links:
                lines.append(f"      Связи: {', '.join(links)}")
        
        lines.append(f"      Тип: {issue_data['issuetype']}")
        lines.append(f"      Автор: {issue_data['reporter']}")
        lines.append(f"      Решение: {issue_data['resolution']}")
        
        return '\n'.join(lines)

if __name__ == "__main__":
    client = JiraClient()
    print("✅ Jira клиент инициализирован")
    print(f"🔗 URL: {client.url}")
    print(f"📧 Email: {client.email}")
    print(f"🔑 Token: {client.token[:10]}..." if client.token else "❌ Токен не задан")
