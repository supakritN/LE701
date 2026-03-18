# 📊 Sensor Simulation & Calculation Tool (LE701)

A web-based application for analyzing and simulating sensor behavior using RF signal data.  
Built with **Python + Streamlit**.

---

## 🚀 Features

- Upload and process simulation files
- Analyze dips and RF characteristics
- View historical runs and restore data
- Interactive tables (filter, sort, export)
- Custom graph plotting (X-Y selection)
- Export results and figures

---

## 🧱 Project Structure

``` text
.
├── README.md
├── core
│   ├── __init__.py
│   ├── auth.py
│   ├── file.py
│   └── result.py
├── db
│   └── upload	
├── math_utils
│   ├── rf_metrics.py
│   ├── signal_feature.py
│   ├── summary_table.py
├── pages
│   ├── 1_Upload.py
│   ├── 2_File_Overview.py
│   ├── 3_History.py
│   ├── 4_Table.py
│   └── 5_Figure.py
├── requirements.txt
└── web_app.py
```

---

## 🛠️ Installation

### Prerequisites

- Python 3.10+
- Git (optional)

---

### Clone Repository

```bash
git clone https://github.com/supakritN/LE701.git
cd LE701
```

---

### Setup Environment

#### Mac / Linux

```bash
python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```

#### Windows (PowerShell)

```powershell
python -m venv myenv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\myenv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## ▶️ Run

#### Mac / Linux

```bash
myenv/bin/streamlit run web_app.py \
  --server.port=8501 \
  --server.address=0.0.0.0
```

#### Windows

```bash
.\myenv\Scripts\streamlit.exe run web_app.py \
  --server.port=8501 \
  --server.address=0.0.0.0
```

---

## 🌐 Access

http://localhost:8501/

---

## 🔐 Default Login

Username: admin  
Password: Le7012026  

---

## 👨‍💻 Author

Supakrit Nithikethkul

# Video
 
- application demo (v0.1): https://www.youtube.com/watch?v=u3RcZc7BvMY
- installation guide: https://www.youtube.com/watch?v=6EfRpunKPk0
- source code: https://github.com/supakritN/LE701
- quick use: https://le701.nithiapp.in.th/ (Deploy on internet)

# Report (For more details on installation and user guide)

- https://drive.google.com/drive/folders/1JPo9ACuPJ8ry_YXR2DzMrnSFU8iGWQwn?usp=sharing
