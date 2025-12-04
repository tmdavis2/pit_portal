# Pit Portal

A comprehensive web portal for the Florida Southern Pit Portal, built with Django. This application provides a platform for real-time social interactions, Esports statistics, event coordination, and more.

## Features

- **User Management**: Custom user authentication and account handling
- **Real-Time Social Chat**: WebSocket-based chat rooms for community interaction
- **Sports Statistics**: Detailed player and team statistics with leaderboards
- **Event Management**: Tools for organizing and tracking athletic events
- **Responsive Design**: Modern UI built with Tailwind CSS
- **Real-Time Communication**: Powered by Django Channels and Redis

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
   Run the provided setup script:
   ```bash
   setup_env.bat
   ```
   This will:
   - Create a virtual environment
   - Install Python dependencies (Django, Django Tailwind, Daphne, Channels)
   - Start a Redis container

3. **Install additional dependencies** (if needed):
   ```bash
   pip install channels-redis
   ```

4. **Navigate to the Django project**:
   ```bash
   cd pit_portal
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

1. **Start the development server**:
   ```bash
   daphne pit_portal.asgi:application
   ```

2. **Access the application**:
   Open your browser and go to `http://127.0.0.1:8000`

## Development

- **Static files**: The project uses CSS. To compile styles:

- **Database**: Uses SQLite by default. For production, configure PostgreSQL or another database in `settings.py`.

## Deployment

The application is configured for deployment locally using Docker

For Docker deployment, build and run the container (Dockerfile assumed to be present).

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