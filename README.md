# Start a single-node elasticsearch instance
docker run --rm --name es01 --net elastic -p 9200:9200 -it -m 1GB -e "xpack.security.enabled=false" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:9.0.2

# Start Kibana (http://localhost:5601)
docker run --rm --name kib01 --net elastic -p 5601:5601 -e ELASTICSEARCH_HOSTS=http://es01:9200 -e "xpack.security.enabled=false" docker.elastic.co/kibana/kibana:9.0.2

# Build the image
docker build . -f Dockerfile -t fastfb:latest

# Run an instance of the image
docker run -it --rm --net elastic --name fb fastfb:latest

# Run fluent-bit
docker exec -it fb fluent-bit -c fluent-bit-config.yaml

# Exercise the FastAPI endpoints
docker exec -it fb curl localhost:8000/metrics
docker exec -it fb curl localhost:8000/fake_endpoint

# Shell into instance to poke around, examine logs, etc.
docker exec -it fb bash

