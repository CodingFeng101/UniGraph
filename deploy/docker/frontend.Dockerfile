FROM node:22-alpine AS build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci \
    && cd /tmp \
    && npm pack lightningcss-linux-x64-musl@1.32.0 \
    && mkdir -p /app/node_modules/lightningcss-linux-x64-musl \
    && tar -xzf lightningcss-linux-x64-musl-1.32.0.tgz \
        -C /app/node_modules/lightningcss-linux-x64-musl --strip-components=1 \
    && npm pack @tailwindcss/oxide-linux-x64-musl@4.3.3 \
    && mkdir -p /app/node_modules/@tailwindcss/oxide-linux-x64-musl \
    && tar -xzf tailwindcss-oxide-linux-x64-musl-4.3.3.tgz \
        -C /app/node_modules/@tailwindcss/oxide-linux-x64-musl --strip-components=1

COPY frontend/ ./
COPY docs/ /docs/
RUN npm run build

FROM nginx:1.27-alpine

RUN apk add --no-cache jq

COPY --from=build /app/dist /usr/share/nginx/html
COPY deploy/nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY deploy/nginx/40-runtime-config.sh /docker-entrypoint.d/40-runtime-config.sh

RUN chmod +x /docker-entrypoint.d/40-runtime-config.sh

EXPOSE 80
