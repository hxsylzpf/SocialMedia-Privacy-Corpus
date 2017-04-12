# privacy
Privacy project with Kylie Geller

## Setup (Ubuntu)
Install system level prerequisites:

    sudo apt-get install build-essential python3-dev python3-tk

Recommend using a virtual environment:

    virtualenv -p python3 venv
    source venv/bin/activate

Make sure you have all `pip` requirements:

    pip install -r requirements.txt

Download English NLP model for `spacy`:

    python -m spacy.en.download

If using API, put API key in a file named api_key:

    echo "API-KEY-HERE" > api_key
