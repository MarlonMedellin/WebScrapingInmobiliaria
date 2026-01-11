# Use Node.js 20 for better Vite compatibility
FROM node:20-alpine

WORKDIR /app

# Copy package files first for caching
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the app
COPY . .

# Expose Vite port
EXPOSE 5173

# Start development server with host exposure
CMD ["npm", "run", "dev", "--", "--host"]
