# Start a single-node elasticsearch instance
docker run --rm --name es01 --net elastic -p 9200:9200 -it -m 1GB -e "xpack.security.enabled=false" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:9.0.2

# Start Kibana
docker run --rm --name kib01 --net elastic -p 5601:5601 -e ELASTICSEARCH_HOSTS=http://es01:9200 -e "xpack.security.enabled=false" docker.elastic.co/kibana/kibana:9.0.2

# Build the image
docker build . -f Dockerfile -t fastfb:latest

# Run an instance of the image
docker run -it --rm --net elastic --name fb fastfb:latest

# Shell into instance
docker exec -it fb bash

    # hit the API
    curl localhost:8000/metrics
    curl localhost:8000/error_endpoint

    # run fluent-bit (parse logs in /tmp/main.log, load them into ES)

