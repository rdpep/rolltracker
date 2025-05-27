# RollTracker

A web app that is designed to collect and track a jiu jitsu practitioner's progress on the mats. This app is intended to provide insights into how someone is training and any trends in their training habits. Rather than training/sparring without any direction or idea of performance, this app can be used after each roll/session to notate performance. Leave the memory to the app! Over time, you will be able to understand what you personal jiu jitsu game is like and where you can improve. 

---

## Features

- User-specific logs and training data
- Dashboard for data visualizations and insights
- Training session search and filtering
- Dark/light mode

---

## Technologies Used

- Python 3
- PythonAnywhere
- `datetime` module
- `collections` module
- `Flask`, `SQLAlchemy`, and `SQLite`

---

## Getting Started

### Prerequisites

- Python 3.x installed
- Required Python packages (install with pip)

```bash
pip install -r requirements.txt
```

---

## Running the App

Through the website primarily: https://rolltracker.pythonanywhere.com/

Locally:
```bash
python app.py
```

Click the link that appears in the terminal. Follow form fields and submit training data. Create an account or login when prompted.

---

## Project Structure

```bash
rolltracker/
├── README.md
├── app.py
├── index.html
├── login.html
├── register.html
├── add_roll.html
├── rolls.html
└── edit_roll.html

```

---

## Future Improvements

- Scale up to larger database support
- Include specialized training recommendations
- UI improvements

---

## Why I Built This

As I have experienced and many other Jiu Jitsu practitioners have experienced as well, most sparring/training sessions come and go without any real retention of what was improved. I decided to create structured training plans whenever I would train and would log the results into my phone's spreadsheet app. However, I found it not intuitive and did not provide clear progression or results. So, the idea for a Jiu Jitsu specific training log app was born and this app is the result. It is still in early stages, and is a small app for a specific issue.  

---

## License

This project is open source and free to use.

---

## Feedback or Ideas?

Feel free to open an issue or reach out with suggestions!
