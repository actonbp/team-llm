FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Default command
CMD ["npm", "run", "dev"]