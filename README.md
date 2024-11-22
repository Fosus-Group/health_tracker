# health_tracker

#### To build and launch the application containers:
```
docker-compose up --build
```
#### To stop and remove the containers, along with the associated volumes:
```
docker-compose down -v
```
#### To connect to the Postgres container and access the `health_tracker` database:
```
docker-compose exec postgres psql -U postgres -d health_tracker 
```
#### To manually apply database migrations using Alembic:
```
docker-compose exec app alembic upgrade head
```
To connect to Postgres and list the tables in the `health_tracker` database:
```
docker-compose exec postgres psql -U postgres -d health_tracker
```
#### Once connected, you can list all tables by running:
```
health_tracker=# \dt
```
#### This command will display the current tables in the `health_tracker` database.

pdm lock --platform linux --append