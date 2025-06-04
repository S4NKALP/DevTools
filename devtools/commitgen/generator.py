"""
Commit message and changelog generation using AI.
"""
from typing import List, Dict, Optional
from ..shared.ai import AIService
from ..shared.config import Config

class CommitGenerator(AIService):
    """AI-powered commit message and changelog generator."""
    
    def __init__(self, config: Config):
        """Initialize commit generator."""
        super().__init__(config)
        
    def generate_commit_message(self, diff: str, temperature: Optional[float] = None) -> str:
        """Generate a commit message from a diff."""
        system_prompt = """You are a helpful AI that generates git commit messages. Keep responses concise and follow the conventional commit format.
        
        Format: type(scope): description
        Types and their emojis:
        - feat: ✨ (new feature)
        - fix: 🐛 (bug fix)
        - docs: 📚 (documentation)
        - style: 💅 (formatting, missing semi colons, etc)
        - refactor: ♻️ (refactoring code)
        - test: ✅ (adding tests)
        - chore: 🔧 (maintenance)
        
        The message should be a single line and follow the conventional commit format strictly. Include the appropriate emoji at the start of the message."""
        
        user_prompt = f"Write a conventional commit message for these changes:\n\n{diff}"
        
        message = self.generate_completion(
            system_prompt,
            user_prompt,
            temperature=temperature
        )
        
        # Clean up the response to ensure it's a valid commit message
        message = message.split('\n')[0].strip()  # Take only the first line
        
        # Ensure the message starts with an emoji
        if not any(emoji in message for emoji in ['✨', '🐛', '📚', '💅', '♻️', '✅', '🔧']):
            # Add appropriate emoji based on the commit type
            if message.startswith('feat'):
                message = '✨ ' + message
            elif message.startswith('fix'):
                message = '🐛 ' + message
            elif message.startswith('docs'):
                message = '📚 ' + message
            elif message.startswith('style'):
                message = '💅 ' + message
            elif message.startswith('refactor'):
                message = '♻️ ' + message
            elif message.startswith('test'):
                message = '✅ ' + message
            elif message.startswith('chore'):
                message = '🔧 ' + message
            else:
                message = '🔧 ' + message  # Default to chore
                
        return message
        
    def generate_changelog(self, commits: List[str], version: str, temperature: Optional[float] = None) -> str:
        """Generate a changelog from a list of commits."""
        system_prompt = """You are a helpful AI that generates changelogs.
        Follow these rules:
        1. Group changes by type (Added, Changed, Fixed, etc.)
        2. Keep descriptions concise but informative
        3. Use past tense
        4. Start each entry with a verb"""
        
        user_prompt = f"Generate a changelog for version {version} with these commits:\n\n" + "\n".join(commits)
        
        return self.generate_completion(
            system_prompt,
            user_prompt,
            temperature=temperature
        ) 