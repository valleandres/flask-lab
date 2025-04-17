# flask-lab

## setup
Add `127.0.0.1 flask.local` to `/etc/hosts` and checkout `http://flask.local/`.

## run unit tests
Just run `docker compose run --rm test`

## run postman tests with cli
Install newman with `npm install -g newman` and run tests with `newman run postman/flask-lab.postman_collection.json`.
