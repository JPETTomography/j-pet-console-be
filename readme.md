# How to run this stuff

go to `common/data_helpers` and get the data first


```
./download_data.sh
```

will download all the needed examplary data to the examplary_data folder.

then simply run

```
docker compose up
```


then see `localhost:8000/docs`
to run full process of running agent, reading data from root, sending it to worker by json and then worker sending it to database use `/send_agent/` method


if the services did not stand up try calling them in this order

```
docker compose up web -d
docker compose up agent -d
docker compose up worker -d
```

or better yet, open each one in separate terminal

```
docker compose up web
docker compose up agent
docker compose up worker
```
