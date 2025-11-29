FROM python:3.13

WORKDIR /app

COPY . .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV DOCKER_ENV=1  
# Define que o app está rodando no Docker

CMD ["python", "main.py"]

#docker build --no-cache -t ccpm .

#docker save --output ccpm.tar ccpm
#scp -i "C:\Users\UXK\Downloads\chave ssh ccpm.pem" C:\Users\UXK\ccpm.tar ubuntu@ec2-18-190-219-178.us-east-2.compute.amazonaws.com:/home/ubuntu/




# Script de conexão SSH (baseado nos comentários acima):
# - No Windows (PowerShell/CMD) usando a chave .pem:
#   scp -i "C:\Users\UXK\Downloads\chave ssh ccpm.pem" C:\Users\UXK\ccpm.tar ubuntu@ec2-18-190-219-178.us-east-2.compute.amazonaws.com:/home/ubuntu/
#   ssh -i "C:\Users\UXK\Downloads\chave ssh ccpm.pem" ubuntu@ec2-18-190-219-178.us-east-2.compute.amazonaws.com
#
# Após conectar ao servidor EC2:
#   sudo docker load -i /home/ubuntu/ccpm.tar
#   sudo docker run --rm -it -p 5000:5000 ccpm
#
# Observações:
# - Ajuste os caminhos da chave e do arquivo .tar conforme necessário.
# - Garanta permissões corretas na chave: chmod 600 ~/.ssh/chave_ccpm.pem
