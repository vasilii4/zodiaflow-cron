FROM alpine:latest
RUN apk --no-cache add curl bash
COPY cron.sh /cron.sh
RUN chmod +x /cron.sh
CMD ["/cron.sh"]
