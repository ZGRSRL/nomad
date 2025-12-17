# Step 1: Build the React Application
FROM node:18-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Step 2: Serve with Nginx
FROM nginx:alpine

# Copy built assets from Step 1
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx config (optional, using default for now but modifying to support React Router)
# We can overwrite the default config to handle SPA routing (fallback to index.html)
RUN echo 'server { \
    listen 8080; \
    root /usr/share/nginx/html; \
    index index.html index.htm; \
    location / { \
    try_files $uri $uri/ /index.html; \
    add_header Cache-Control "no-cache, no-store, must-revalidate"; \
    add_header Pragma "no-cache"; \
    add_header Expires "0"; \
    } \
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ { \
    expires 1y; \
    add_header Cache-Control "public, immutable"; \
    } \
    }' > /etc/nginx/conf.d/default.conf

# Expose port (Cloud Run defaults to 8080)
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
