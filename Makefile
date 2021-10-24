install-deps:
	pip install -r requirements.txt

setup-dev-environment:
	virtualenv venv

run-dev:
	flask run

run-prd:
	gunicorn wsgi:app -b 0.0.0.0:5000
