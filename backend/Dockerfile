# Use OpenJDK 17 base image
FROM openjdk:17-jdk-slim

# Set working directory
WORKDIR /app

# Copy project
COPY . .

# Build using Maven
RUN apt-get update && apt-get install -y maven
RUN mvn -q -DskipTests package

# Run the Spring Boot app
CMD ["java", "-jar", "target/code-review-backend.jar"]

