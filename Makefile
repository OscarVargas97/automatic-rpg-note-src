.PHONY: install migrate makemigrations run shell

install:
	uv sync

migrate:
	uv run python manage.py migrate

makemigrations:
	uv run python manage.py makemigrations

run:
	uv run python manage.py runserver

shell:
	uv run python manage.py shell
