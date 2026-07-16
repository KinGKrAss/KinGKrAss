FROM node:22-alpine

WORKDIR /app
COPY apps/web/package.json /app/package.json
COPY apps/web/tsconfig.json /app/tsconfig.json
COPY apps/web/next.config.ts /app/next.config.ts
COPY apps/web/next-env.d.ts /app/next-env.d.ts
COPY apps/web/app /app/app

RUN npm install
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "start"]
