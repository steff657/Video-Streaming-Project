# YourTubeFlix - Video Streaming Platform

YourTubeFlix is a full-stack Django video streaming platform where users can sign up, upload and manage videos, and engage with content through likes, dislikes, and comments. It supports practical creator controls like public/private/unlisted visibility, soft-delete for comments, and personal video management (edit/delete), while also including moderation-oriented features such as reporting and admin review workflows. The site is built with a responsive Bootstrap 5 interface, uses django-allauth for authentication, supports ffmpeg-powered media handling, and is structured for both local development and production deployment with PostgreSQL/S3-ready configuration.A Django-based video streaming platform with user authentication, video uploads, comments, and reactions.

YourTubeFlix was created as part of a Capstone project for a Code Institute bootcamp.

The deployed website can be found here:- [](https://yourtubeflix-b9bff9094aa7.herokuapp.com/)

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
- **Database:** SQLite, PostgreSQL
- **Authentication:** django-allauth
- **Video Processing:** ffmpeg

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

### Video Reaction

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

MAX_UPLOAD_SIZE=209715200
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
heroku config:set AWS_S3_REGION_NAME="your region"
```

Without external storage, uploaded files can disappear after dyno restart.

### Post-Deploy Health Check

Run this command after deployment to verify there are no pending migrations
and critical tables (`core_profile`, `core_video`, `core_report`) exist:

```bash
python manage.py check_deploy_health
```

On Heroku:

```bash
heroku run python manage.py check_deploy_health --app your-app-name
```

## Agile Methodology and User Stories

Project planning and progress tracking were managed in an Agile board
(Kanban style) using backlog, in-progress, review, and done columns.

### User stories implemented

1. As a visitor, I can browse recent public videos so I can discover content.
2. As a user, I can register and log in so I can upload and manage videos.
3. As a user, I can upload a video with title, description, tags, and
   visibility so I can share content.
4. As a user, I can edit or delete my own videos so I can keep my content
   up to date.
5. As a user, I can react to and comment on videos so I can engage with
   content.
6. As a user, I can edit/delete my own comments so I can correct mistakes.
7. As a user, I can update profile/account settings so I can manage identity
   and credentials.
8. As a user, I can report inappropriate videos so moderators can review them.
9. As an admin/staff user, I can review reports and remove violating content.
10. As an admin/staff user, I can remove abusive accounts and keep an audit
    log of admin actions.

## UX Process and Artifacts

### Design approach

- Mobile-first layout with progressive enhancement for desktop.
- Clear information hierarchy: top navigation, searchable content grid,
  focused video detail page, and task-oriented forms.
- Consistent visual language based on Bootstrap plus custom site styles.

### Key UX decisions

- Added persistent login-state controls in the header/sidebar so users can
  always see account status and available actions.
- Prioritized discoverability with search and "Recently Uploaded" defaults.
- Reduced form friction with inline validation and clear field labels.
- Used responsive Grid/Flex patterns to keep layout functional on small screens.

### Accessibility notes

- Semantic page regions are used (`header`, `main`, article cards, form labels).
- Alternative text is provided for rendered profile/video images.
- Focus and input states are styled for keyboard users.
- Color palette aims for readable contrast in primary workflows.

## Wireframes

### Core and Account Screens

![Home Search Wireframe](wireframes/Home%20_%20Search%20-%20Wireframe.png)
![Video Detail Wireframe](wireframes/Video%20Detail%20-%20Wireframe.png)
![Upload Video Wireframe](wireframes/Upload%20Video%20-%20Wireframe.png)
![My Videos Wireframe](wireframes/My%20Videos%20-%20Wireframe.png)
![Edit Video Wireframe](wireframes/Edit%20Video%20-%20Wireframe.png)
![Delete Video Wireframe](wireframes/Delete%20Video%20-%20Wireframe.png)
![Profile Detail Wireframe](wireframes/Profile%20Detail%20-%20Wireframe.png)
![Edit Profile Wireframe](wireframes/Edit%20Profile%20-%20Wireframe.png)
![Account Settings Wireframe](wireframes/Account%20Settings%20-%20Wireframe.png)
![Login Wireframe](wireframes/Login%20-%20Wireframe.png)
![Sign Up Wireframe](wireframes/Sign%20Up%20-%20Wireframe.png)
![Logout Wireframe](wireframes/Logout%20-%20Wireframe.png)

### Admin and Error Screens

![Admin Users Wireframe](wireframes/Admin%20Users%20-%20Wireframe.png)
![Admin Reports Wireframe](wireframes/Admin%20Reports%20-%20Wireframe.png)
![Not Allowed 403 Wireframe](wireframes/Not%20Allowed%20%28403%29%20-%20Wireframe.png)
![404 Wireframe](wireframes/404-wireframe.png)

## Lighthouse Testing Snapshot

### Home Page Lighthouse Report Screenshot

![Lighthouse Home Report Screenshot](testing/lighthouse/home.report.screenshot.png)

## Testing Documentation

### Test strategy

- Automated Django tests cover critical backend workflows:
  - Upload validation
  - Comment validation
  - Profile/account updates
  - Reporting/moderation
  - Guest access restrictions
  - Deployment health command
- Manual checks were used for responsive behavior and interaction flows in
  the browser (upload progress, reactions, comments, admin actions).

### Automated test execution

```bash
python manage.py test
```

Latest local run result:

- 13 tests executed
- 13 passed
- 0 failed

### Deployment/security checks

```bash
python manage.py check --deploy
python manage.py check_deploy_health
```

## AI Usage Reflection

AI tooling was used as an engineering assistant for targeted implementation
and review tasks.

### Code creation

- Helped draft and refine CRUD-related view/form patterns and template logic.
- Assisted with structuring model constraints and validation flows.

### Debugging

- Helped identify edge cases in upload handling, auth flows, and moderation
  paths by suggesting focused checks.

### Performance and UX optimization

- Suggested improvements to reduce repeated work (query filtering patterns,
  concise view responses, and lightweight front-end updates).
- Supported responsive UI refinements and clearer feedback messaging.

### Workflow impact

- Improved development speed for repetitive scaffolding tasks.
- Kept focus on outcome quality by accelerating iteration and review.
- Final implementation and validation decisions were kept developer-led.

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
