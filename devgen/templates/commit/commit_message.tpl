You write Conventional Commits. Output ONLY the message — no preamble, no labels, no quotes, no markdown.

Format:
<type>[optional scope][optional !]: <description>
[optional blank line]
[optional body]
[optional blank line]
[optional footer(s)]

types: feat fix refactor perf docs test build ci chore style
scope: {% if group_name and group_name != 'root' %}({{ group_name }}){% else %}optional{% endif %}{% if use_emoji %} (prefix description with one matching emoji){% endif %}

Examples:
feat: add email notifications on new direct messages
feat(shopping cart): add the amazing button
feat!: remove ticket list endpoint
refers to JIRA-1337
BREAKING CHANGE: ticket endpoints no longer supports list all entities.
fix(shopping-cart): prevent order an empty shopping cart
fix(api): fix wrong calculation of request body checksum
fix: add missing parameter to service call
The error occurred due to <reasons>.
perf: decrease memory footprint for determine unique visitors by using HyperLogLog
build: update dependencies
build(release): bump version to 1.0.0
refactor: implement fibonacci number calculation as recursion
style: remove empty line

{{ diff_text }}{{ context }}
