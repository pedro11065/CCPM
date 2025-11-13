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
#docker load -i /home/ubuntu/ccpm.tar

#docker run --rm -it -p 5000:5000 ccpm