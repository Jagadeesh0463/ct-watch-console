# Build context is the repo root (see docker-compose.yml).
FROM node:20-slim AS build

WORKDIR /app

COPY frontend/package.json ./
RUN npm install --no-audit --no-fund

COPY frontend/ .

# Baked into the built JS bundle at build time -- the browser calls this URL
# directly, so it must be reachable from the host, not just other containers.
ARG VITE_API_BASE_URL=http://localhost:5000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
