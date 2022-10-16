
# Development requirements
An environment with a working docker-compose.<br/>
This project was tested on macOS with docker-compose version 1.29.0, build 07737305
___
<br/>

## API structure

Get All Agents - GET /agents

Add Agent - POST /agents

Get All Messages - GET /agents/{agent_name}/messages (optional query parameters start_date/end_date/new)

Add Message - POST /agents/{agent_name}/messages

Delete Messages - DELETE /agents/{agent_name}/messages
___
<br/>

## Build and start the REST API with postgres DB
<code>docker-compose up -d --build</code>
___
<br/>

# Run databse migrations
<code>docker-compose exec web alembic upgrade head</code>
___
<br/>

## Running tests
Make sure to run the database migrations before running tests.<br>
For manuall testing see "Interacting with the REST API" bellow<br><br>
<code>docker-compose exec web pytest .</code><br>
Tests are currently running against the dev databse.<br>
This was helpfull for developmemt but tests should not leave traces like
this for a real application.
<br>
<br>
To remove/reset the application run:<br>
<code>docker-compose down</code><br>
<code>docker-compose up -d --build</code><br>
<code>docker-compose exec web alembic upgrade head</code><br>
___
<br/>

## Interacting with the REST API
After the container has started all informations about routes and Schemas can be found
and manually tested via the OpenAPI client at http://localhost:8004/docs <br/>
Routes can also be tested locally via CURL.

Create agent<br>
<code>
curl -X 'POST' \
  'http://localhost:8004/agents' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "jonas"
}'
</code><br>
Retrive agent<br>
<code>
curl 'http://localhost:8004/agents'
</code>

___
<br/>

## (optional) start the REST API locally
- Create a virtual envirinment at the root of this project <code> python3.10 -m venv venv </code>
- initialize the virtualenvironment <code>source /venv/bin/activate</code>
- install dependecies locally <code>pip install -r requirements-txt</code>
- set the DATABASE_URL  <code>export DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/web_db</code>
- start the web server <code>uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 8008</code>
___
<br/>

## (optional) Connect to postgres DB
Localy with psql installed:
<code>psql -h localhost --username=postgres --dbname=web_db</code>

Via docker-compose:
<code>docker-compose exec db psql --username=postgres --dbname=web_db</code>
___

## generate new migrations with alembic
<code>docker-compose exec web alembic revision --autogenerate -m "details of revision"</code>

## What is the state of this project
It's a proof of concept, running fast-api with sqlalchemy async.
- Automatic tests have not been prioritized.
- API Client error messages could also be improved.
- Dockerfile could be improved (adding nondefault user / and security validation)