# Base image
FROM apache/airflow:2.10.1

# Switch to root user to ensure appropriate permissions
USER root

# Install necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    apt-transport-https \
    java-common

# Download and install OpenJDK 11 (Amazon Corretto)
RUN curl -L -o /tmp/corretto-11.deb https://corretto.aws/downloads/latest/amazon-corretto-11-x64-linux-jdk.deb && \
    dpkg -i /tmp/corretto-11.deb || apt-get -f install -y && \
    rm /tmp/corretto-11.deb


# Install Apache Spark
ENV SPARK_VERSION=3.5.2
ENV HADOOP_VERSION=3

# Download Apache Spark
RUN mkdir -p /opt && \
    curl --retry 5 --continue-at - -O https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz && \
    tar -xzf spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz -C /opt/ && \
    mv /opt/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION /opt/airflowspark && \
    rm spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz

# Set environment variables for Java, Spark, and Hadoop
ENV JAVA_HOME=/usr/lib/jvm/java-11-amazon-corretto
ENV SPARK_HOME=/opt/airflowspark
ENV HADOOP_HOME=/opt/airflowhadoop
ENV PATH=$JAVA_HOME/bin:$SPARK_HOME/bin:$HADOOP_HOME/bin:$PATH

# Create directory for logs and adjust permissions
RUN mkdir -p /opt/airflow/log && chown -R airflow: /opt/airflow/log

# Copy requirements.txt file to install additional Python dependencies
COPY requirements.txt /requirements.txt

# Switch to 'airflow' user for pip installation
USER airflow

# Install pip dependencies as 'airflow' user
RUN pip install --upgrade pip && pip install --no-cache-dir -r /requirements.txt

# Expose Spark ports, if needed
EXPOSE 8080 7077 8081

# Set default command to start Airflow
CMD ["airflow", "standalone"]
