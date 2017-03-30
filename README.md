# privacy
Privacy project with Kylie Geller

## Setup
Recommend using a virtual environment:

    virtualenv -p python3 venv
    source venv/bin/activate

Install the Guardian API by copying the library to the virtual environment's `lib` folder (for most up-to-date version, run the install instructions from [here](git clone https://github.com/prabhath6/theguardian-api-python.git
)):

    pip install -r requirements.txt
    cp -r theguardian venv/lib/python3.5  # or version of python

Put API key in a file named api_key:

    echo "API-KEY-HERE" > api_key
