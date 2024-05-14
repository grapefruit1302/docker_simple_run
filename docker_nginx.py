import os
import subprocess

def main():
    project_name = input("Назва директорії: ")

    os.makedirs(project_name, exist_ok=True)
    os.chdir(project_name)

    server_name = input("Ім'я сервера: ")
    port = input("Порт для запуску контейнера (за замовчуванням 8080): ")
    php_version = input("Версія PHP: ")

    with open("index.php", "w") as f:
        f.write('<?php phpinfo(); ?>')

    nginx_conf = f"""
server {{
    listen {port};
    server_name {server_name};
    root /var/www/html;
    index index.php index.html index.htm;

    location / {{
        try_files $uri $uri/ /index.php?$query_string;
    }}

    location ~ \.php$ {{
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_pass unix:/var/run/php/php{php_version}-fpm.sock;
        fastcgi_index index.php;
    }}
}}
"""
    with open("nginx.conf", "w") as f:
        f.write(nginx_conf)

    dockerfile_content = f"""
FROM php:{php_version}-fpm
RUN apt-get update && apt-get install -y nginx
COPY nginx.conf /etc/nginx/sites-available/default
WORKDIR /var/www/html
COPY . /var/www/html/
"""

    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)

    build_container = input("Побудувати контейнер? (так/ні): ")
    if build_container.lower() == "так":
        tag_name = input("Назва тегу для контейнера: ")
        os.system(f"docker build -t {tag_name} .")

    run_container = input("Запустити контейнер? (так/ні): ")
    if run_container.lower() == "так":
        os.system(f"docker run -d -p {port}:80 --name {project_name} {tag_name}")

        container_ip = get_container_ip(project_name)

        with open("/etc/hosts", "a") as hosts_file:
            hosts_file.write(f"\n{container_ip} {server_name}")
    os.system("docker ps")

def get_container_ip(container_name_or_id):
    result = subprocess.run(['docker', 'inspect', '-f', '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}', container_name_or_id], capture_output=True, text=True)

    if result.returncode == 0:
        return result.stdout.strip()
    else:
        print("Помилка: Неможливо отримати IP-адресу контейнера")
        return None

if __name__ == "__main__":
    main()
