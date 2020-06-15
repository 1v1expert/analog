ifdef ENVIRONMENT
	ENVIRONMENT := $(ENVIRONMENT)
else
	ENVIRONMENT := local
endif

build:
	docker-compose -f ${ENVIRONMENT}.yml build

up:
	docker-compose -f ${ENVIRONMENT}.yml up

down:
	docker-compose -f ${ENVIRONMENT}.yml down

start:
	docker-compose -f ${ENVIRONMENT}.yml build && \
	docker-compose -f ${ENVIRONMENT}.yml down && \
	docker-compose -f ${ENVIRONMENT}.yml kill && \
	docker-compose -f ${ENVIRONMENT}.yml up -d

logs:
	docker-compose -f ${ENVIRONMENT}.yml logs

migrations:
	docker-compose -f ${ENVIRONMENT}.yml run --rm django python manage.py makemigrations && \
	docker-compose -f ${ENVIRONMENT}.yml run --rm django python manage.py migrate

test:
	docker-compose -f ${ENVIRONMENT}.yml down	
	docker-compose -f ${ENVIRONMENT}.yml up -d chrome hub
	docker-compose -f ${ENVIRONMENT}.yml run --rm django pytest . -s
	docker-compose -f ${ENVIRONMENT}.yml down	

shell:
	docker-compose -f ${ENVIRONMENT}.yml run --rm django python manage.py shell

superuser:
	docker-compose -f ${ENVIRONMENT}.yml run --rm django python manage.py createsuperuser

reset-db:
	docker-compose -f ${ENVIRONMENT}.yml down && \
	docker-compose -f ${ENVIRONMENT}.yml run --rm django python manage.py reset_db && \
	docker-compose -f ${ENVIRONMENT}.yml run --rm django python manage.py makemigrations && \
	docker-compose -f ${ENVIRONMENT}.yml run --rm django python manage.py migrate

reset-db-hard:
	find . -path "*/migrations/*.py" -not -name "__init__.py" -not -path "*/contrib/*" -delete && \
	find . -path "*/migrations/*.pyc" -path "*/migrations/__pycache__/*.pyc" -delete && \
	docker-compose -f ${ENVIRONMENT}.yml down && \
	docker-compose -f ${ENVIRONMENT}.yml run --rm django python manage.py reset_db && \
	docker-compose -f ${ENVIRONMENT}.yml run --rm django python manage.py makemigrations && \
	docker-compose -f ${ENVIRONMENT}.yml run --rm django python manage.py migrate

mypy:
	docker-compose -f ${ENVIRONMENT}.yml run --rm django mypy .

flake8:
	docker-compose -f ${ENVIRONMENT}.yml run --rm django flake8 .

black:
	docker-compose -f ${ENVIRONMENT}.yml run --rm django black --target-version py36 .

coverage:
	docker-compose -f ${ENVIRONMENT}.yml run --rm django coverage run -m py.test
	docker-compose -f ${ENVIRONMENT}.yml run --rm django coverage report
	docker-compose -f ${ENVIRONMENT}.yml run --rm django coverage html

pre-commit:
	docker-compose -f ${ENVIRONMENT}.yml run --rm django mypy .
	docker-compose -f ${ENVIRONMENT}.yml run --rm django flake8 .
	docker-compose -f ${ENVIRONMENT}.yml run --rm django black --target-version py36 .
	docker-compose -f ${ENVIRONMENT}.yml run --rm django coverage run -m py.test
	docker-compose -f ${ENVIRONMENT}.yml run --rm django coverage report
	docker-compose -f ${ENVIRONMENT}.yml run --rm django coverage html

remove-pycache:
	find . -type f -name "*.py[co]" -delete && \
	find . -type d -name "__pycache__" -delete

vizualization:
	docker-compose -f ${ENVIRONMENT}.yml run --rm django python manage.py graph_models --pygraphviz -a -g -o visualized_models.svg -L en-us -e

