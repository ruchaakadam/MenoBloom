# 🌸 MenoBloom

### A Personalized Menopause Wellness & Support Platform

MenoBloom is a web-based wellness platform designed to help women better understand and manage their menopause journey through symptom tracking, nutrition tracking, reminders, family support, mental wellness support, and private journaling.

The platform focuses on one important principle:

> **Support, don't take over.**

MenoBloom gives women control over their information while allowing trusted family members to provide meaningful support when the woman chooses to share information.

---

## 🌷 Features

### 👩‍🦰 Personalized Woman Dashboard

- Personalized menopause journey
- Menopause stage information
- Symptom overview
- Nutrition overview
- Reminder tracking
- Wellness activity tracking

### 🌸 Symptom Tracking

Users can record symptoms such as:

- Hot flashes
- Night sweats
- Sleep problems
- Mood changes
- Anxiety
- Fatigue
- Headaches
- Joint and muscle discomfort
- Brain fog
- Vaginal dryness
- Urinary changes

Each symptom can include:

- Severity
- Frequency
- Date
- Notes

### 📊 Symptom Analysis

MenoBloom provides visual analysis of recorded symptoms.

The analysis includes:

- Symptom frequency
- Symptom trends
- Individual symptom activity
- Recent symptom patterns

---

### 🥗 Nutrition Tracking

Users can record meals and nutritional information including:

- Calories
- Protein
- Calcium
- Carbohydrates
- Fat
- Fiber
- Meal type
- Portion / quantity
- Health benefits
- Menopause-related nutritional benefits

---

### 🔔 Health Reminders

Users can create and manage reminders for:

- Doctor appointments
- Medication
- Cancer screening
- Cervical screening
- Bone health
- Routine health checks
- Follow-ups
- Custom reminders

Users can mark reminders as completed or delete them.

---

### 👨‍👩‍👧 Family Support

MenoBloom allows a woman to securely connect her account with a trusted family member.

The woman receives a unique connection code which can be used by the family member to request a connection.

The woman controls what information can be shared:

- Symptoms
- Nutrition
- Reminders

Health information is not automatically exposed simply because two accounts are connected.

---

### 🧠 Mental Wellness Support

MenoBloom includes a mental-support chatbot designed to provide a safe space where users can:

- Express how they are feeling
- Talk through everyday emotional difficulties
- Receive supportive responses
- Reflect on their thoughts

The chatbot is intended for emotional support and is **not a replacement for professional mental-health care or emergency services.**

---

### 🔐 Private Secret Notes

Users can privately write down:

- Feelings
- Thoughts
- Personal reflections
- Experiences
- Things they may not want to share with others

These notes are associated with the user's account and are not part of family sharing.

---

## 🔒 Privacy by Design

MenoBloom follows a consent-based approach to family support.

A connected family member does not automatically receive access to private health information.

The woman decides what information is shared.

Private notes remain separate from family-sharing functionality.

---

## 🛠️ Technology Stack

### Backend

- Python
- Django
- Django ORM
- SQLite for local development
- PostgreSQL for production

### Frontend

- HTML
- CSS
- JavaScript
- Responsive UI

### Deployment

- Render
- Gunicorn
- PostgreSQL
- WhiteNoise

### Version Control

- Git
- GitHub

---

## 📁 Project Structure

```text
menopause-care/
│
├── manage.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── tracker/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── migrations/
│   └── templates/
│       └── tracker/
│
├── static/
│
├── requirements.txt
│
├── build.sh
│
├── render.yaml
│
└── README.md
