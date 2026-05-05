FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install
RUN npm install react react-dom

COPY . .

# 🔥 ПОЛНЫЕ ЛОГИ npm
ENV CI=false
ENV NPM_CONFIG_LOGLEVEL=verbose

# 🔥 принудительно показываем ошибки
RUN npm run build --debug

FROM nginx:stable-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]