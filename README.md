# PATA
_aka_
## Python Analytics Test Assignment
___
Simple project written on FastAPI to prove that I'm capable of 
engineering complex REST-API CRUD and analytics solutions.

## How to run?
1. Create your own `.env` file (use `sample.env` to understand how it should look like)
2. Bring everything up with:
```shell
docker compose up -d --build
```
3. Check health of your instance:
```shell
curl -f http://localhost:8000/health
```
4. Create new user (it would automatically be assigned admin privileges):
```shell
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "login": "admin1",
    "email": "admin1@example.com",
    "password": "SuperSecret123"
  }'
```
5. I know you're already tired of using curl, so go to the apps `/docs` and enjoy working with GUI!
