# Frontend Dockerfile
FROM node:18-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

# Run in dev mode for easy hackathon debugging
CMD ["npm", "run", "dev", "--", "--host"]
