# Stage 1: Build frontend
FROM node:20-slim AS frontend-builder

WORKDIR /build
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile
COPY . .
RUN yarn build

# Stage 2: Serve with nginx
FROM nginx:1.27-alpine AS frontend
COPY --from=frontend-builder /build/dist /usr/share/nginx/html
COPY nginx.frontend.conf /etc/nginx/conf.d/default.conf
EXPOSE 8081
CMD ["nginx", "-g", "daemon off;"]