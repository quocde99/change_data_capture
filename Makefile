up:
	docker compose up -d --build
	

remove-minio-data:
	rm -rf ./minio/data

compose-down:
	docker compose down -v

monitor-down:
	docker-compose -f docker-compose-monitoring.yml down

down: compose-down remove-minio-data

down-monitor: monitor-down

minio-ui:
	open http://localhost:9001

pg:
	pgcli -h localhost -p 2345 -U postgres -d postgres

PG_SRC_CONNECTOR=./connectors/pg-src-connector.json
S3_SINK_CONNECTOR=./connectors/s3-sink.json

check_port:
	@echo "Checking if localhost:8083 is available..." ; \
	nc -z localhost 8083 && echo "localhost:8083 is available, proceeding..." || (echo "localhost:8083 is not available, aborting..." && exit 1)

pg-src: check_port
	@echo "Creating PG source connector..." ; \
	echo "Connector configuration:" ; \
	cat $(PG_SRC_CONNECTOR) ; \
	curl -v -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" localhost:8083/connectors/ -d '@$(PG_SRC_CONNECTOR)'

s3-sink: check_port
	@echo "Creating S3 sink connector..." ; \
	echo "Connector configuration:" ; \
	cat $(S3_SINK_CONNECTOR) ; \
	curl -v -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" localhost:8083/connectors/ -d '@$(S3_SINK_CONNECTOR)'
monitor:
	docker-compose -f docker-compose-monitoring.yml up -d

connectors: pg-src s3-sink