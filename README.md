# Weather Data Scraping

**Description:**
Web Scraping, Data Processing, and CSV Export.

**Getting Started:**

1. **Clone the repository:**

```bash
   git clone git@github.com:Av007/weather.git
```
or 
```
curl -L http://github.com/Av007/weather/archive/main.zip
```

2 **Installation**

a. Create Virtual Envirounment
```
python -m venv venv
source venv/bin/activate
```
b. Install dependencies:
```
pip install -e .
```
4. **Run the project**

```
flask cache-init # will work without this command
flask run
``` 

5. **See results**

Results you can see in browser:

 * *Running on http://127.0.0.1:5000*
 * file located [weather_data.csv](report/weather_data.csv)
