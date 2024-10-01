# Read Me First #

This is the order to work through this material. The code is marked up for what you need to implement to understand how RMQ or Kafka provides those patterns.

If an  exercises are marked [Not Available] there may be code but we are not currently covering in the course. They may be covered in some presentations of the course where we are trying it out.

## Precursors ##

These have speaker notes accompanying the slides

Quick Start Rabbit Kafka.pptx

## Patterns and Exercises ##

## Streams ##

[Not Available]pub-sub-stream-exercise.pptx
Exercise: Pub-Sub-Stream

### Adding the MySQL database

Please ensure you add the following to the Docker Compose file

```
 mysql:
    image: mysql
    ports:
      - "3306:3306"
    volumes:
      - ./mysql-data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: "root"

volumes:
  mysql-data:
    driver: local      
```

### Working with a MySQL database

Your IDE will probably be able to work with a MySQL Db.

In Visual Code use: MySQL by Weijan Chen

A stand-alone alternative is: https://www.mysql.com/products/workbench/


### Python MySQL Dependencies

You will need to install the MySQL package

```

brew install mysql pkg-config

```

to be able to install

```

https://github.com/PyMySQL/mysqlclient?tab=readme-ov-file#macos-homebrew

```


### Creating the Database

Use

```
docker exec -i pub-sub-stream-mysql-1 sh -s < Database/create_database.sh
```

where `pub-sub-stream-mysql-1' is the container name. Use `docker ps` to find this.

### Kafka Topics

To ensure creation of Kafka topics automatically when you produce to them ensure that withing your Dockerfile we have set

```
KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"

```



### Activity and Correlation ###

[Not Available] request-reply-exercise.pptx
Exercise: Request-Reply -- sends a message and then blocks waiting for a reply. Can also use a correlation id, and non-blocking approach in production code

[Not Available] 
## Fat and Skinny ##

conversations.pptx
Exercise: Event Carried State Transfer

## Conversations ##

Exercise: Routing Slip -- Message understands it's flow down the pipeline.
