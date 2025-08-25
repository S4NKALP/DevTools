"""
Project type detection for gitignore generation.
"""

import os
from typing import List, Dict, Set


class ProjectDetector:
    """Detect project types based on file patterns."""

    # File patterns for different project types
    PROJECT_PATTERNS = {
        # Languages
        "python": ["*.py", "requirements.txt", "setup.py", "Pipfile", "pyproject.toml"],
        "javascript": ["package.json", "*.js", "*.jsx", "*.ts", "*.tsx"],
        "typescript": ["tsconfig.json", "*.ts", "*.tsx"],
        "java": ["*.java", "pom.xml", "build.gradle", "*.class"],
        "kotlin": ["*.kt", "*.kts"],
        "go": ["go.mod", "go.sum", "*.go"],
        "rust": ["Cargo.toml", "Cargo.lock", "*.rs"],
        "ruby": ["Gemfile", "*.rb", "*.gemspec"],
        "php": ["composer.json", "*.php"],
        "csharp": ["*.cs", "*.csproj", "*.sln"],
        "swift": ["*.swift", "*.xcodeproj"],
        "objective-c": ["*.m", "*.h", "*.mm"],
        # Frameworks
        "django": ["manage.py", "wsgi.py", "asgi.py"],
        "flask": ["app.py", "flask_app.py"],
        "fastapi": ["main.py", "app.py"],
        "react": ["src/App.js", "src/App.tsx"],
        "vue": ["vue.config.js", "*.vue"],
        "angular": ["angular.json", "tsconfig.json"],
        "spring": ["application.properties", "application.yml"],
        "laravel": ["artisan", "composer.json"],
        "rails": ["config/routes.rb", "Gemfile"],
        "express": ["app.js", "server.js"],
        "next": ["next.config.js"],
        "nuxt": ["nuxt.config.js"],
        # Build Tools
        "maven": ["pom.xml"],
        "gradle": ["build.gradle", "settings.gradle"],
        "npm": ["package.json"],
        "yarn": ["yarn.lock"],
        "pip": ["requirements.txt"],
        "poetry": ["pyproject.toml"],
        "cargo": ["Cargo.toml"],
        "composer": ["composer.json"],
        # IDEs and Editors
        "vscode": [".vscode/settings.json"],
        "intellij": [".idea/workspace.xml"],
        "eclipse": [".project", ".classpath"],
        "vim": [".vimrc", ".vim/"],
        "emacs": [".emacs", ".emacs.d/"],
        "sublime": ["*.sublime-project", "*.sublime-workspace"],
        "atom": [".atom/"],
        # Operating Systems
        "windows": ["*.exe", "*.dll", "*.sys"],
        "macos": [".DS_Store", "*.app"],
        "linux": ["*.so", "*.o"],
        # Testing Frameworks
        "jest": ["jest.config.js"],
        "pytest": ["pytest.ini", "conftest.py"],
        "junit": ["junit.xml"],
        "mocha": ["mocha.opts"],
        # Documentation
        "sphinx": ["docs/conf.py"],
        "mkdocs": ["mkdocs.yml"],
        "docusaurus": ["docusaurus.config.js"],
        # Databases
        "postgresql": ["*.sql", "*.dump"],
        "mysql": ["*.sql", "*.dump"],
        "mongodb": ["*.bson"],
        "sqlite": ["*.db", "*.sqlite"],
        # Cloud Platforms
        "aws": [".aws/", "aws.json"],
        "azure": ["azure.yaml", "azure.json"],
        "gcp": ["gcloud.json"],
        # Containerization
        "docker": ["Dockerfile", "docker-compose.yml"],
        "kubernetes": ["k8s/", "*.yaml"],
        # CI/CD
        "github-actions": [".github/workflows/"],
        "gitlab-ci": [".gitlab-ci.yml"],
        "jenkins": ["Jenkinsfile"],
        "travis": [".travis.yml"],
        "circleci": [".circleci/config.yml"],
        # Static Site Generators
        "jekyll": ["_config.yml"],
        "hugo": ["config.toml", "config.yaml"],
        "gatsby": ["gatsby-config.js"],
        # Game Development
        "unity": ["*.unity", "*.unityproj"],
        "unreal": ["*.uproject"],
        # Machine Learning
        "tensorflow": ["*.pb", "*.h5"],
        "pytorch": ["*.pt", "*.pth"],
        "scikit-learn": ["*.joblib"],
    }

    def __init__(self, directory: str = "."):
        """Initialize project detector.

        Args:
            directory: Directory to scan
        """
        self.directory = directory

    def detect_project_types(self) -> List[str]:
        """Detect project types in the directory.

        Returns:
            List of detected project types
        """
        detected_types = set()

        # Scan directory for files
        for root, _, files in os.walk(self.directory):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.directory)

                # Check each project type's patterns
                for type_, patterns in self.PROJECT_PATTERNS.items():
                    if any(
                        self._matches_pattern(rel_path, pattern) for pattern in patterns
                    ):
                        detected_types.add(type_)

        return sorted(list(detected_types))

    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if a path matches a pattern.

        Args:
            path: Path to check
            pattern: Pattern to match

        Returns:
            True if path matches pattern
        """
        # Handle directory patterns
        if pattern.endswith("/"):
            return path.startswith(pattern[:-1])

        # Handle wildcard patterns
        if "*" in pattern:
            import fnmatch

            return fnmatch.fnmatch(path, pattern)

        # Handle exact matches
        return path == pattern
