# AI Job Application Bot

An open-source AI-powered job application bot that automates the process of searching and applying for jobs using AI technologies.

## Features

- Automated job search and application using Selenium and undetected-chromedriver
- AI-powered resume and cover letter customization using OpenAI
- Web interface for monitoring applications and job status
- Stealth mode to avoid bot detection
- Database storage for tracking applications
- Configurable job search parameters and automation settings

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
```

2. Activate the virtual environment:
- Windows:
```bash
.\.venv\Scripts\Activate.ps1
```
- Unix/MacOS:
```bash
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
- Copy `.env.example` to `.env`
- Add your OpenAI API key and other configuration settings

## Usage

1. Start the API server:
```bash
cd src
uvicorn api:app --reload
```

2. Configure your job search preferences in `config.py`

3. Run the job application bot (coming soon)

## Legal Notice

This tool is for educational purposes only. Using automated tools to interact with job platforms may violate their terms of service. Use responsibly and at your own risk.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
