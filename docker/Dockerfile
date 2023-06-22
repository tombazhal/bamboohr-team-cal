FROM python:3.9

WORKDIR /app

COPY dofunc/packages/bhrtools/bhrteamcal/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#CMD ["tail", "-f", "/dev/null"]
CMD ["python", "main.py"]
