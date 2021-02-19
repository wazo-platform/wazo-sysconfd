test-setup: test-image egg-info

test-image:
	docker build -t wazoplatform/wazo-sysconfd ..
	docker build --no-cache -t wazoplatform/wazo-sysconfd-tests -f docker/Dockerfile-sysconfd-test ..

egg-info:
	cd .. && python3 setup.py egg_info

test:
	pytest -x

.PHONY: test-setup test test-image
