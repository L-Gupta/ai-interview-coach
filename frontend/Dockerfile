# --- Build stage ---
FROM node:20-alpine AS build
WORKDIR /app

COPY package*.json ./
# package-lock.json is out of sync with package.json, so npm ci would fail
RUN npm install --no-audit --no-fund

COPY . .

# REACT_APP_* values are baked into the bundle at build time and are used by
# the browser, so this must be the host-facing backend URL.
ARG REACT_APP_API_URL=http://localhost:1600
ENV REACT_APP_API_URL=$REACT_APP_API_URL
RUN npm run build

# --- Serve stage ---
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 1500
