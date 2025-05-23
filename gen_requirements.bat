pip-compile pyproject.toml
pip-compile pyproject.toml --extra api -o requirements-api.txt
pip-compile pyproject.toml --all-extras -o requirements-dev.txt