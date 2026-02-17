# YourTubeFlix - Video Streaming Platform

A Django-based video streaming platform with user authentication, video uploads, comments, and reactions.

## Features

- 🎬 **Video Upload & Management** - Upload, edit, and delete videos
- 🔐 **User Authentication** - Sign up, login, and account management with django-allauth
- 👍 **Reactions** - Like/dislike videos
- 💬 **Comments** - Comment on videos with soft-delete functionality
- 🔒 **Privacy Controls** - Public, Private, and Unlisted visibility options
- 📱 **Responsive Design** - Mobile-friendly interface with Bootstrap 5
- 🎨 **Modern UI** - Gradient backgrounds and custom styling

## Technology Stack

- **Backend:** Django 6.0.2
- **Frontend:** Bootstrap 5, HTMX
- **Database:** SQLite (development), PostgreSQL (recommended for production)
- **Authentication:** django-allauth
- **Video Processing:** ffmpeg (optional, for thumbnail generation)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/Video-Streaming-Project.git
cd Video-Streaming-Project
```

### 2. Create a virtual environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup environment variables
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and set your configuration
# At minimum, set DJANGO_SECRET_KEY to a secure value
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create a superuser (admin account)
```bash
python manage.py createsuperuser
```

### 7. Run the development server
```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## Project Structure

```text
Video-Streaming-Project/
├── core/                 # Main app
│   ├── migrations/       # Database migrations
│   ├── static/           # CSS, JS, images
│   ├── templates/        # HTML templates
│   ├── admin.py          # Admin configuration
│   ├── forms.py          # Form definitions
│   ├── models.py         # Database models
│   ├── urls.py           # URL routing
│   └── views.py          # View logic
├── yourtubeflix/         # Project settings package
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL config
│   └── wsgi.py           # WSGI application
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
├── Procfile              # Heroku web process
├── runtime.txt           # Heroku Python runtime
└── .env.example          # Environment variables template
```

## Models

### Video
- `owner` - ForeignKey to User
- `title` - Video title
- `description` - Video description
- `tags` - JSON field for tags
- `visibility` - Public/Private/Unlisted
- `video_file` - Uploaded video file
- `thumbnail` - Auto-generated thumbnail
- `created_at` - Creation timestamp

### Comment
- `video` - ForeignKey to Video
- `user` - ForeignKey to User
- `comment_text` - Comment content
- `created_at` - Creation timestamp
- `is_deleted` - Soft delete flag
- `deleted_at` - Deletion timestamp

### VideoReaction
- `video` - ForeignKey to Video
- `user` - ForeignKey to User
- `value` - Like or Dislike
- `created_at` - Creation timestamp

## API Endpoints

### Public
- `GET /` - Homepage
- `GET /video/<id>/` - View video detail
- `GET /accounts/` - Authentication pages

### Authenticated User
- `GET /upload/` - Upload page
- `POST /upload/` - Submit video upload
- `GET /my-videos/` - List user's videos
- `GET /video/<id>/edit/` - Edit video page
- `POST /video/<id>/edit/` - Submit video edits
- `GET /video/<id>/delete/` - Delete confirmation page
- `POST /video/<id>/delete/` - Delete video
- `POST /video/<id>/react/` - Like/dislike video
- `POST /video/<id>/comment/` - Post comment
- `POST /comment/<id>/delete/` - Delete comment

## Configuration

Key settings in `.env`:

```ini
DEBUG=True                          # Set to False in production
DJANGO_SECRET_KEY=your-key-here    # Generate a secure key
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000

MAX_UPLOAD_SIZE=209715200          # 200 MB in bytes
ALLOWED_VIDEO_EXTENSIONS=mp4,mov,webm,mkv
```

## Production Deployment

### Important Security Changes:
1. Set `DEBUG=False` in `.env`
2. Generate a secure `DJANGO_SECRET_KEY`
3. Set `ALLOWED_HOSTS` to your domain
4. Use PostgreSQL or another production database
5. Configure email backend for password resets
6. Use a production WSGI server (Gunicorn)
7. Configure HTTPS with SSL/TLS
8. Use environment variables for sensitive data
9. Use object storage for uploaded media files (Heroku disk is ephemeral)

### Deployment Example (Gunicorn + Nginx):
```bash
# Install production dependencies
pip install gunicorn whitenoise

# Run with Gunicorn
gunicorn yourtubeflix.wsgi:application --bind 0.0.0.0:8000
```

### Heroku Media Storage (S3)
Set these config vars in Heroku:

```bash
heroku config:set USE_S3=True
heroku config:set AWS_ACCESS_KEY_ID=...
heroku config:set AWS_SECRET_ACCESS_KEY=...
heroku config:set AWS_STORAGE_BUCKET_NAME=...
heroku config:set AWS_S3_REGION_NAME=us-east-1
```

Without external storage, uploaded files can disappear after dyno restart.

## Requirements for Features

- **FFmpeg/FFprobe:** Install for automatic thumbnail generation and resolution validation
  - Windows: `choco install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Ubuntu: `apt-get install ffmpeg`
  - Heroku: add an `Aptfile` with `ffmpeg` and enable the apt buildpack:
    - `heroku buildpacks:add --index 1 heroku-community/apt`

## Troubleshooting

### Database errors
```bash
python manage.py migrate --run-syncdb
```

### Static files not loading
```bash
python manage.py collectstatic
```

### FFmpeg/FFprobe not found
- Ensure `ffmpeg` and `ffprobe` are installed and in your PATH
- Thumbnails are generated with ffmpeg if available
- Resolution validation is enforced with ffprobe if available

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
