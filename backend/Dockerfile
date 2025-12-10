# Use Temurin JDK 17 (Render-friendly)
FROM eclipse-temurin:17-jdk

# Set working directory
WORKDIR /app

# Copy Maven wrapper and pom.xml first for caching
COPY pom.xml .

# Copy the project source
COPY src ./src

# Install Maven + build the JAR
RUN apt-get update && apt-get install -y maven
RUN mvn -q clean package -DskipTests

# Run the JAR
CMD ["java", "-jar", "target/code-review-0.0.1-SNAPSHOT.jar"]
