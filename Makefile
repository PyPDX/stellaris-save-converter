build: freeze
	sam build

docker_build_images:
	docker-compose build

freeze_hello_world: docker_build_images
	docker-compose run --rm hello_world pip freeze > hello_world/requirements.txt

freeze: freeze_hello_world
