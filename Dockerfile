FROM python:3.12-alpine
WORKDIR /app
STOPSIGNAL SIGTERM
ENV ENV=/app/.profile

RUN <<-EOF
	apk add git tzdata
	pip install -U pip setuptools
	addgroup --gid 1000 rpgbot
	adduser --disabled-password --home /app --uid 1000 --ingroup rpgbot rpgbot
	chown -R rpgbot:rpgbot /app
EOF

USER rpgbot
COPY pyproject.toml /app/
COPY config.toml /app/
COPY requirements /app/requirements
COPY realm_bot /app/realm_bot

RUN <<-EOF
	mkdir -p /app/data
	pip install --no-cache --no-warn-script-location -Ue .
EOF

ENTRYPOINT [ "/usr/local/bin/python", "-m", "aethersprite" ]
