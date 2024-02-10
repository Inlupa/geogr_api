# FROM postgres:16-bullseye

# LABEL maintainer="PostGIS Project - https://postgis.net" \
#       org.opencontainers.image.description="PostGIS 3.4.1+dfsg-1.pgdg110+1 spatial database extension with PostgreSQL 16 bullseye" \
#       org.opencontainers.image.source="https://github.com/postgis/docker-postgis"

# ENV POSTGIS_MAJOR 3
# ENV POSTGIS_VERSION 3.4.1+dfsg-1.pgdg110+1

# RUN apt-get update \
#       && apt-cache showpkg postgresql-$PG_MAJOR-postgis-$POSTGIS_MAJOR \
#       && apt-get install -y --no-install-recommends \
#            ca-certificates \
#            \
#            postgresql-$PG_MAJOR-postgis-$POSTGIS_MAJOR=$POSTGIS_VERSION \
#            postgresql-$PG_MAJOR-postgis-$POSTGIS_MAJOR-scripts \
#       && rm -rf /var/lib/apt/lists/*

# RUN mkdir -p /docker-entrypoint-initdb.d
# COPY ./initdb-postgis.sh /docker-entrypoint-initdb.d/10_postgis.sh
# COPY ./update-postgis.sh /usr/local/bin
FROM postgres:14.1
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get  install -y postgresql-14-postgis-3
CMD ["/usr/local/bin/docker-entrypoint.sh","postgres"]
