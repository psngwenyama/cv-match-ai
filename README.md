# CV-Match AI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Django](https://img.shields.io/badge/Django-6.0-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)](https://www.mysql.com/)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-purple.svg)](https://deepmind.google/technologies/gemini/)

> **An intelligent web application that uses AI to help job seekers tailor their CVs to specific job descriptions.**

CV-Match AI analyzes job descriptions, matches requirements against a user's master profile, and generates ATS-optimized, tailored CVs in seconds instead of hours.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [AI Integration](#ai-integration)
- [Contributors](#contributors)
- [License](#license)

---

## 🎯 Overview

**CV-Match AI** is a full-stack web application that leverages Large Language Models (LLMs) to automatically tailor CVs to specific job descriptions.

**Built With:**
- **Frontend:** React 18 + TailwindCSS
- **Backend:** Django 6.0 + Django REST Framework
- **Database:** MySQL 8.0 (production) / SQLite (development)
- **AI:** Google Gemini API (primary) + OpenAI API (fallback)

**Time Saved:** 2-3 hours manual tailoring → 10 seconds automated

---

## ❓ Problem Statement

| Problem | Impact |
|---------|--------|
| **Time-consuming** | 2-3 hours per application |
| **ATS rejection** | 75% of applications rejected by software before human review |
| **Poor optimization** | Candidates don't know which skills to highlight |
| **Missed opportunities** | Generic CVs fail to demonstrate genuine interest |

---

## ✨ Features

| Feature | Status | Description |
|---------|--------|-------------|
| User Authentication | ✅ | JWT-based registration/login with refresh tokens |
| Password Reset | ✅ | Email-based password recovery |
| Master Profile | ✅ | Work experience, education, skills, projects, certifications, languages |
| Job Description Analysis | ✅ | AI extracts key skills, responsibilities, requirements |
| AI CV Generation | ✅ | Tailored CV with relevance scoring |
| Multiple Templates | ✅ | User-uploadable DOCX/PDF templates |
| CV Export | ✅ | PDF and DOCX download |
| CV History | ✅ | Track all generated CVs |
| Application Tracking | ✅ | Mark jobs as applied/interviewing/offer |
| Dashboard Analytics | ✅ | Stats on CVs, match scores, applications |

---

## 🛠 Technology Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.2.0 | UI framework |
| Vite | 4.0+ | Build tool |
| TailwindCSS | 3.3+ | Styling |
| React Router DOM | 6.0+ | Navigation |
| React Hook Form | 7.0+ | Form management |
| Axios | 1.4+ | API communication |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Django | 6.0 | Web framework |
| Django REST Framework | 3.14+ | API framework |
| MySQL | 8.0+ | Production database |
| SQLite | 3.x | Development database |
| JWT (SimpleJWT) | 5.2+ | Authentication |
| Celery | 5.3+ | Async tasks (planned) |

### AI & DevOps
| Technology | Purpose |
|------------|---------|
| Google Gemini API | Primary AI provider (free tier) |
| OpenAI API | Fallback provider |
| Docker | Containerization |
| GitHub Actions | CI/CD pipeline |

---

## 🏗 Architecture
