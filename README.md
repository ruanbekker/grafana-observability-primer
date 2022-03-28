# grafana-observability-primer
Grafana Observability Primer

## stack

Deploy:

```bash
docker-compose up -d --build
```

## k6

Create user:

```bash
docker run --rm -i --network=docknet loadimpact/k6 run --quiet - < k6lib/http_post.js
```

Run tests to perform get requests:

```bash
docker run --rm -i --network=docknet loadimpact/k6 run --quiet - < k6lib/http_gets.js
```

## usage

API Usage:

```
# list all users
curl -H 'Content-Type: application/json' http://localhost:5000/users
```

```
# create user
curl -XPOST -H 'Content-Type: application/json' http://localhost:5000/users -d '{"username": "ruan", "email": "ruan@localhost"}'
```
