database-down:
	docker-compose down

database-up:
	docker-compose up

airflow-build:
	chmod +x airflow.sh
	./airflow.sh