FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir . \
    && python -m spacy download pt_core_news_sm \
    && python -c "import spacy; spacy.load('pt_core_news_sm')"

RUN groupadd --system --gid 10001 communitylab \
    && useradd --system --uid 10001 --gid communitylab \
        --no-create-home --shell /usr/sbin/nologin communitylab

USER 10001:10001

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3)" || exit 1

CMD ["streamlit", "run", "app/main.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
