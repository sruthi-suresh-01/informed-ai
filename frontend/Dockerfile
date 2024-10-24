# FROM node:16 as build
# WORKDIR /app
# COPY package.json package-lock.json ./
# RUN npm install
# COPY . .
# RUN npm run build

# # Production stage
# FROM nginx:alpine
# COPY --from=build /app/build /usr/share/nginx/html
# EXPOSE 80
# CMD ["nginx", "-g", "daemon off;"]



FROM node:18 AS builder

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# # Copy patches for npm packages before running npm ci
# COPY patches ./patches/

# Install dependencies
RUN npm ci

# Copy the entire project
COPY . .

# Build the application
RUN npm run build

# ---- Serve Stage ----
FROM nginx:stable-alpine3.19-slim AS server

# Copy the build output to replace the default nginx contents.
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 to the Docker host so we can access it
EXPOSE 80

# The default command runs Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]
