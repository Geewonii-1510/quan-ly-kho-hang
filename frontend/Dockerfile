# Frontend Dockerfile (multi-stage build)
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies / Cài đặt thư viện
COPY package*.json ./
RUN npm ci

# Build app / Build ứng dụng
COPY . .
RUN npm run build

# Production stage / Giai đoạn production
FROM nginx:alpine

# Copy build output / Sao chép output build
COPY --from=build /app/dist /usr/share/nginx/html

# Nginx config for SPA routing
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location /api { \
        proxy_pass http://backend:8000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
