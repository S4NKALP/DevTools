"""License generator module."""

import os
import requests
from typing import Dict, List, Optional
from ..shared.config import Config


class LicenseGenerator:
    """License generator using GitHub API."""

    def __init__(self):
        """Initialize the license generator."""
        self.api_base_url = "https://api.github.com"
        self.config = Config()

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        # Try to get token from config first
        token = self.config.get("github_token")

        # Then try environment variable
        if not token:
            token = os.environ.get("GITHUB_TOKEN")

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DevTools/1.0",
        }

        if token:
            headers["Authorization"] = f"Bearer {token}"

        return headers

    def fetch_available_licenses(self) -> List[Dict]:
        """Fetch available licenses from GitHub API."""
        try:
            # Get headers with token
            headers = self._get_headers()

            # First check rate limit
            rate_limit_response = requests.get(
                f"{self.api_base_url}/rate_limit", headers=headers
            )
            if rate_limit_response.status_code == 200:
                rate_limit_data = rate_limit_response.json()

                # Check if we have remaining requests
                remaining = (
                    rate_limit_data.get("resources", {})
                    .get("core", {})
                    .get("remaining", 0)
                )
                if remaining == 0:
                    raise ValueError(
                        "GitHub API rate limit exceeded. Please set a GitHub token using:\ndevtools config set GITHUB_TOKEN YOUR_GITHUB_TOKEN"
                    )

            # Fetch list of licenses
            response = requests.get(f"{self.api_base_url}/licenses", headers=headers)

            if response.status_code == 403:
                raise ValueError(
                    "GitHub API rate limit exceeded. Please set a GitHub token using:\ndevtools config set GITHUB_TOKEN YOUR_GITHUB_TOKEN"
                )

            response.raise_for_status()
            licenses = response.json()

            # Fetch detailed info for each license
            detailed_licenses = []
            for license in licenses:
                try:
                    license_response = requests.get(
                        f"{self.api_base_url}/licenses/{license['key']}",
                        headers=headers,
                    )
                    if license_response.status_code == 200:
                        license_data = license_response.json()
                        detailed_licenses.append(
                            {
                                "key": license_data["key"],
                                "name": license_data["name"],
                                "description": license_data.get(
                                    "description", "No description available"
                                ),
                                "permissions": license_data.get("permissions", []),
                                "conditions": license_data.get("conditions", []),
                                "limitations": license_data.get("limitations", []),
                            }
                        )
                except Exception:
                    continue

            return detailed_licenses

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error fetching licenses: {str(e)}")

    def get_license_template(self, license_type: str) -> str:
        """Get license template from GitHub API."""
        try:
            response = requests.get(
                f"{self.api_base_url}/licenses/{license_type}",
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return response.json()["body"]
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error fetching license template: {str(e)}")

    def generate_license(
        self, license_type: str, author: str, year: Optional[int] = None
    ) -> str:
        """Generate license content with author and year."""
        template = self.get_license_template(license_type)

        # Replace placeholders
        content = template.replace("[year]", str(year) if year else "")
        content = content.replace("[fullname]", author)

        return content


# Create a singleton instance
license_generator = LicenseGenerator()


def generate_license(
    license_type: str,
    author: str,
    year: Optional[int] = None,
    output_file: str = "LICENSE",
) -> str:
    """Generate a license file."""
    try:
        # Generate license content
        content = license_generator.generate_license(license_type, author, year)

        # Write to file
        with open(output_file, "w") as f:
            f.write(content)

        return output_file

    except Exception as e:
        raise ValueError(f"Error generating license: {str(e)}")
