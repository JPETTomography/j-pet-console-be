# How to run this stuff

go to `common/data_helpers` and get the data first


```
python download_data.py
```

will download all the needed examplary data to the examplary_data folder.

then simply run

```
docker compose up
```

to run full process of running agent, reading data from root, sending it to worker by json and then worker sending it to database use `/send_agent/` method
