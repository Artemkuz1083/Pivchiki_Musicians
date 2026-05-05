FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# 🔥 включаем максимум логов для CI
ENV CI=true
ENV NPM_CONFIG_LOGLEVEL=verbose

# 🔥 вывод зависимостей (помогает ловить сломанные пакеты)
RUN npm ls || true

# 🔥 билд с подробным выводом
RUN npm run build || (echo "❌ BUILD FAILED" && exit 1)


FROM nginx:stable-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]