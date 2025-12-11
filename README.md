# Pit Portal

A comprehensive web portal for the Florida Southern Pit Portal, built with Django. This application provides a platform for real-time social interactions, Esports statistics, event coordination, and more.

## Features

- **User Management**: Custom user authentication and account handling
- **Real-Time Social Chat**: WebSocket-based chat rooms for community interaction
- **Game Statistics**: Detailed player and game statistics with leaderboards
- **Event Management**: Tools for organizing and tracking athletic events
- **Responsive Design**: Modern UI built with Tailwind CSS
- **Real-Time Communication**: Powered by Django Channels and Redis

## Screenshots

- **Pit Portal Home Page**
![Screenshot of the Pit Portal home page](pages/static/pages/images/home_page.png)
- **Pit Portal Stats Page**
![Screenshot of the Pit Portal stats page](pages/static/pages/images/stats_page.png)
- **Pit Portal Social Page**
![Screenshot of the Pit Portal social page](pages/static/pages/images/social_page.png)
- **Pit Portal Events Page**
![Screenshot of the Pit Portal events page](pages/static/pages/images/events_page.png)

## Tech Stack

- **Backend**: Django 5.2.5, Django Channels, Daphne (ASGI server)
- **Database**: SQLite (development), Redis (for channel layers)
- **Frontend**: HTML, Custom CSS (Tailwind CSS configured but not actively used for styling)
- **Real-Time**: WebSockets via Django Channels
- **Deployment**: Docker, Fly.io

## Prerequisites

- Python 3.8+
- Node.js (for Tailwind CSS compilation)
- Docker (for Redis)
- Git

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd pit_portal2
   ```

2. **Set up the environment**:
   Create a virtual environment and activate it (commands vary by platform):
   - **Windows**:
     ```bash
     python -m venv .venv
     source .venv/Scripts/activate
     ```
   - **macOS/Linux**:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```
   Install Python dependencies:
   ```bash
   pip install django django-tailwind daphne channels channels-redis Pillow whitenoise
   ```

3. **Navigate to the Django project**:
   ```bash
   cd pit_portal
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

1. **Start the development server**:
   ```bash
   daphne pit_portal.asgi:application -p 8001
   ```

2. **Access the application**:
   Open your browser and go to `http://127.0.0.1:8001`

## Development

- **Static files**: The project uses CSS. 

- **Database**: Uses SQLite by default. For production, configure PostgreSQL or another database in `settings.py`.

## Deployment

The application is configured for deployment locally 

## Project Structure

- `accounts/`: User authentication and management
- `pages/`: Static pages and home
- `social/`: Real-time chat functionality
- `stats/`:  Statistics and leaderboards
- `events/`: Event management
- `theme/`: Tailwind CSS configuration and static files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For questions or issues, please open an issue on the GitHub repository.