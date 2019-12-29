build: freeze
	sam build

docker_build_images:
	docker-compose build

freeze_converter: docker_build_images
	docker-compose run --rm converter pip freeze > converter/requirements.txt

freeze_dev: docker_build_images
	docker-compose run --rm test pip freeze > requirements.txt

freeze: freeze_converter freeze_dev

test: freeze
	docker-compose run --rm test

deploy: build
	sam deploy
