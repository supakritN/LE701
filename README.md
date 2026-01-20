# LE701

version 0.1 youtube: https://youtu.be/u3RcZc7BvMY

# Prerequisite

- python
- git

# installation

``` bash
git clone https://github.com/supakritN/LE701.git
cd LE701
python -m venv .venv
```

For mac/linux

``` bash
source .venv/bin/activate
```

For windows
``` bash
source .venv/Script/activate
```

Deploy application

``` bash
pip install -r requirements.txt
.venv/bin/streamlit run web_app.py \
  --server.port=8501 \
  --server.address=0.0.0.0
```
