# ===== Stage 1: Build =====
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /build
# settings.xml định tuyến Maven Central qua mirror Google (tránh 403 từ repo.maven.apache.org)
COPY settings.xml /root/.m2/settings.xml
COPY pom.xml .
RUN mvn -q -B -Dmaven.wagon.http.retryHandler.count=3 dependency:go-offline
COPY src ./src
RUN mvn -q -B -Dmaven.wagon.http.retryHandler.count=3 clean package -DskipTests

# ===== Stage 2: Runtime =====
FROM eclipse-temurin:17-jre
WORKDIR /app
# Python + thư viện cho các script:
#  - openpyxl: trích xuất Excel (POST /api/import/excel)
#  - reportlab + mysql.connector: sinh báo cáo PDF/Slide (/api/report/export-*)
#  - fonts-dejavu: font Unicode (tiếng Việt) cho reportlab
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
         python3 \
         python3-openpyxl \
         python3-reportlab \
         python3-mysql.connector \
         fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*
COPY --from=build /build/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
