build: freeze validate
	sam build

docker_build_images:
	docker-compose build

freeze: docker_build_images
	docker-compose run --rm converter pip freeze > converter/requirements.txt
	docker-compose run --rm upload pip freeze > upload/requirements.txt
	docker-compose run --rm test pip freeze > requirements.txt

validate:
	sam validate

test: freeze validate
	docker-compose run --rm test

deploy: test build
	sam deploy

start: build
	sam local start-api
