# LE701

video update
 
application demo (v0.1): https://www.youtube.com/watch?v=u3RcZc7BvMY
installation guide: https://www.youtube.com/watch?v=6EfRpunKPk0
 
source code: https://github.com/supakritN/LE701
quick use: https://le701.nithiapp.in.th/ (Deploy ทิ้งไว้ สามารถเข้าใช้งานผ่าน internet)

# Prerequisite

- python
- git

# installation

``` bash
git clone https://github.com/supakritN/LE701.git
cd LE701
python3 -m venv .venv
```

If no venv module, For Ubuntu (please check the python version before, for example python version 3.10)

``` bash
python -V
sudo apt install python3.10-venv
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
