# Response Collector service
1. Make sure RabbitMQ is running. If not, then:  
```docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.10-management```
2. Make sure redis server is active  
3. Build Docker container for Response Collector service  
```docker build -t "res-collector" .```
4. Run the container  
```docker run -it --network=host "res-collector"```