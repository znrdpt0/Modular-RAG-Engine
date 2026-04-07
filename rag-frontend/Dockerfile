# STAGE 1: İnşaat Aşaması
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# STAGE 2: Servis Aşaması (Nginx)
# Sadece derlenmiş dosyaları alıp hafif bir web sunucusuna (Nginx) koyuyoruz
FROM nginx:stable-alpine
# React'in çıktılarını Nginx'in yayın klasörüne kopyala
COPY --from=build /app/dist /usr/share/nginx/html
# Eğer React Router kullanıyorsan Nginx konfigürasyonu gerekebilir, şimdilik standart bırakıyoruz
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]