# Stage 1: Install dependencies
FROM node:18-alpine AS deps
WORKDIR /app

# Copy package.json and lock file
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./

# Install dependencies based on the lock file found
RUN if [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
    elif [ -f package-lock.json ]; then npm ci; \
    elif [ -f pnpm-lock.yaml ]; then npm install -g pnpm && pnpm install --frozen-lockfile; \
    else echo "No lockfile found. Please add one." && exit 1; fi

# Stage 2: Build the application
FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
# Copy only build-essential files and directories
COPY package.json package-lock.json* next.config.mjs tsconfig.json postcss.config.mjs eslint.config.mjs ./
COPY public ./public
COPY src ./src

ARG NEXT_PUBLIC_GOOGLE_CLIENT_ID
ENV NEXT_PUBLIC_GOOGLE_CLIENT_ID ${NEXT_PUBLIC_GOOGLE_CLIENT_ID}
ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL ${NEXT_PUBLIC_API_BASE_URL}
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build
# Removed debug line

# Stage 3: Production image (using Next.js standalone output)
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone /app/
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs
EXPOSE 3000
ENV PORT 3000
CMD ["node", "server.js"]