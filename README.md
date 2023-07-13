## Docker Stacks

Creamos primero la imagen del cluster de Apache Spark:
```
docker build -t cluster-apache-spark:3.2.1 .
```

Componemos el docker:
```
docker compose up -d
```

### 1. Kafka

Creamos un topic de Kafka llamado FV
```
docker exec -it redpanda rpk topic create FV
```

Accedemos por consola al contenedor Kafka:
```
docker exec -it redpanda /bin/bash 
```

Y ejecutamos dentro del contenedor el siguiente comando para añadir al topic FV el siguiente json:
```
rpk topic produce FV < /tmp/data/FV.json
```

### 2. Spark


Accedemos por consola al contenedor Spark Master:
```
docker exec -it spark-master /bin/bash 
```

Ejecutamos la query:
```
python3 /opt/spark-apps/GroupbyDate.py
```

En la siguiente URL podeis consultar los trabajos realizados

```http://localhost:9095```
