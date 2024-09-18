FROM apache/airflow:2.10.1

# Alterar para o usuário root para garantir permissões adequadas
USER root

# Instalar dependências necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    apt-transport-https \
    java-common

# Baixar e instalar o OpenJDK 11 (Amazon Corretto)
RUN curl -L -o /tmp/corretto-11.deb https://corretto.aws/downloads/latest/amazon-corretto-11-x64-linux-jdk.deb && \
    dpkg -i /tmp/corretto-11.deb || apt-get -f install -y && \
    rm /tmp/corretto-11.deb

# Instalar o Apache Spark
ENV SPARK_VERSION=3.5.2
ENV HADOOP_VERSION=3

# Baixar o Apache Spark com retry e continue-at para garantir download completo
RUN mkdir -p /opt && \
    curl -O --retry 5 --continue-at - https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz && \
    tar -xzf spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz -C /opt/ && \
    mv /opt/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION /opt/airflowspark && \
    rm spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz

# Definir variáveis de ambiente para o Java, Spark e Hadoop
ENV JAVA_HOME=/usr/lib/jvm/java-11-amazon-corretto
ENV SPARK_HOME=/opt/airflowspark
ENV HADOOP_HOME=/opt/airflowhadoop
ENV PATH=$JAVA_HOME/bin:$SPARK_HOME/bin:$HADOOP_HOME/bin:$PATH

RUN mkdir -p /opt/airflow/log && chown -R airflow: /opt/airflow/log


# Copiar o arquivo requirements.txt
COPY requirements.txt /requirements.txt

# Alternar para o usuário 'airflow' para instalação do pip
USER airflow

# Instalar dependências do pip como usuário 'airflow'
RUN pip install --upgrade pip && pip install --no-cache-dir -r /requirements.txt

# Expor portas do Spark, se necessário
EXPOSE 8080 7077 8081

# Definir o comando padrão
CMD ["airflow", "standalone"]
