"""Internationalization (i18n) system"""

import json
import os
from constants import CWD


class I18n:
    """Manages translations"""

    def __init__(self):
        self.current_language = 'th'
        self.translations = {}
        self.load('th')

    def load(self, language: str) -> bool:
        """Load translation file"""
        path = os.path.join(CWD, 'i18n', f'{language}.json')
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            self.current_language = language
            return True
        except Exception as e:
            print(f"Failed to load translation for {language}: {e}")
            return False

    def t(self, key: str, **kwargs) -> str:
        """Translate with string formatting"""
        text = self.translations.get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text

    def get_available_languages(self) -> list:
        """Get list of available languages"""
        i18n_dir = os.path.join(CWD, 'i18n')
        languages = []
        for file in os.listdir(i18n_dir):
            if file.endswith('.json'):
                languages.append(file[:-5])
        return languages


# Singleton instance
i18n = I18n()


def t(key: str, **kwargs) -> str:
    """Shortcut translation function"""
    return i18n.t(key, **kwargs)
