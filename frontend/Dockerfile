FROM node:18-alpine

WORKDIR /app

# Copia i file di dipendenze prima per sfruttare la cache di Docker
COPY package*.json ./
RUN npm install

# Copia il resto dell'applicazione
COPY . .

EXPOSE 3000

# Avvia Vite impostando host per accettare connessioni dall'esterno del container
CMD ["npm", "run", "dev", "--", "--host"]
