test:
	@pre-commit run --all-files

install:
	@pip3 install --upgrade pip setuptools wheel
	@sleep 3
	@pip install -U -r requirements.txt

run:
	@python3 -m Curse

clean:
	@rm -rf Curse/logs
	@pyclean .
