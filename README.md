# flask-lab

## setup
Add `127.0.0.1 flask.local` to `/etc/hosts` and checkout `http://flask.local/`.

## run unit tests
Just run `docker compose run --rm test`

## run postman tests with cli
Install newman with `npm install -g newman` and run tests with `newman run postman/flask-lab.postman_collection.json`.

## development

### venv (virtualenv)
```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
deactivate
```

### pylint
```bash
pip3 install pylint
pylint --generate-rcfile > .pylintrc
vim .pylintrc
```
vs code settings:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.pylintArgs": ["--rcfile=.pylintrc"]
}
```