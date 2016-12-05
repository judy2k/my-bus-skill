all: deploy

zappa_settings.json:
	zappa init

deploy: zappa_settings.json
	aws s3 cp credentials.json $(shell jq .dev.remote_env zappa_settings.json)
	zappa update dev

.PHONY: all deploy
