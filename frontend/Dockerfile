FROM node:18-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ARG REACT_APP_API_SOURCE
ENV REACT_APP_API_SOURCE=$REACT_APP_API_SOURCE

EXPOSE 3000

CMD ["npm", "start"]
