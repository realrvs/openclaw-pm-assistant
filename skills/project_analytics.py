import json
from pathlib import Path

PROJECTS_FILE = Path.home() / '.openclaw/workspace/data/projects.json'

def load_projects():
    with open(PROJECTS_FILE) as f:
        return json.load(f)['projects']

def get_status():
    projects = load_projects()
    output = "Статус проектов:\n"
    for p in projects:
        output += f"Проект: {p['name']}\n"
        output += f"  Статус: {p['status']}\n"
        output += f"  Команда: {p['team_size']} чел.\n"
        output += f"  Технологии: {', '.join(p['tech_stack'])}\n"
        output += f"  Риски: {', '.join(p['risks'])}\n\n"
    return output

if __name__ == "__main__":
    print(get_status())
