package: freeze validate
	sam build

build:
	docker-compose build

freeze: build
	docker-compose run --rm -T converter pip freeze > converter/requirements.txt
	docker-compose run --rm -T presign pip freeze > presign/requirements.txt
	docker-compose run --rm -T test pip freeze > requirements.txt

validate:
	sam validate

test: freeze validate
	docker-compose run --rm test

deploy_tags := `[ -n "$(tags)" ] && echo "--tags $(tags)" || echo ""`
deploy: test package
	sam deploy $(deploy_tags)

deploy_guided: test package
	sam deploy --guided $(deploy_tags)

start: package
	sam local start-api
