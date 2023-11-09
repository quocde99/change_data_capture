FROM postgres
ADD ./container/postgres/init.sql /docker-entrypoint-initdb.d/
ENTRYPOINT ["docker-entrypoint.sh"]
EXPOSE 2345
CMD ["postgres"]