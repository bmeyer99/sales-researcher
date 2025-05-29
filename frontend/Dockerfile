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

ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build # Or: yarn build / pnpm build

# Stage 3: Production image (using Next.js standalone output)
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone/server.js ./server.js
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT 3000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD node /app/server.js || exit 1
CMD ["node", "/app/server.js"]