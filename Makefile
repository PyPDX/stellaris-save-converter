package: freeze validate
	sam build

build:
	docker-compose build

freeze: build
	docker-compose run --rm converter pip freeze > converter/requirements.txt
	docker-compose run --rm upload pip freeze > upload/requirements.txt
	docker-compose run --rm test pip freeze > requirements.txt

validate:
	sam validate

test: freeze validate
	docker-compose run --rm test

deploy: test package
	sam deploy

start: package
	sam local start-api
