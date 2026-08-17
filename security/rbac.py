import os
from pathlib import Path
import json

class TelegramRBAC:
    def __init__(self):
        self.config_path = Path.home() / '.openclaw/workspace/security/allowed_users.json'
        self.allowed_users = self._load_config()
    
    def _load_config(self):
        if not self.config_path.exists():
            default_config = {
                "allowed_users": [
                    int(os.getenv('TELEGRAM_ADMIN_ID', '0'))
                ]
            }
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            print("⚠️ Создан файл allowed_users.json. Добавьте ваш Telegram ID!")
            return default_config
        with open(self.config_path) as f:
            return json.load(f)
    
    def check_access(self, user_id: int) -> bool:
        return user_id in self.allowed_users.get('allowed_users', [])
    
    def get_accessible_projects(self, user_id: int) -> list:
        if self.check_access(user_id):
            return ["RUS", "DIT", "MOW", "VTB", "SBER"]
        return []

if __name__ == "__main__":
    rbac = TelegramRBAC()
    print("✅ RBAC модуль инициализирован")
    print("📋 Текущие пользователи:", rbac.allowed_users)
