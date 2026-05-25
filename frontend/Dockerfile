# Stage 1: Build frontend
FROM node:20-slim AS frontend-builder

WORKDIR /build

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .

# Production defaults — override via docker-compose build args if needed
ARG VITE_KEYCLOAK_URL=https://www.keytomarvel.com
ARG VITE_KEYCLOAK_REALM=catobigato
ARG VITE_KEYCLOAK_CLIENT_ID=catobigato
ARG VITE_API_BASE_URL=https://catobigato.com

# Expose build args as env vars so Vite picks them up during yarn build
ENV VITE_KEYCLOAK_URL=$VITE_KEYCLOAK_URL
ENV VITE_KEYCLOAK_REALM=$VITE_KEYCLOAK_REALM
ENV VITE_KEYCLOAK_CLIENT_ID=$VITE_KEYCLOAK_CLIENT_ID
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN yarn build

# Stage 2: Serve with nginx
FROM nginx:1.27-alpine AS frontend
COPY --from=frontend-builder /build/dist /usr/share/nginx/html
COPY nginx.frontend.conf /etc/nginx/conf.d/default.conf
EXPOSE 8081
CMD ["nginx", "-g", "daemon off;"]
