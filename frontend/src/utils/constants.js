export const JOB_STATUS = {
  GENERATED: 'generated',
  APPLIED: 'applied',
  INTERVIEWING: 'interviewing',
  REJECTED: 'rejected',
  OFFER: 'offer',
};

export const TEMPLATES = {
  MODERN: 'modern',
  PROFESSIONAL: 'professional',
  CREATIVE: 'creative',
  MINIMAL: 'minimal',
};

export const SKILL_LEVELS = {
  BEGINNER: 'beginner',
  INTERMEDIATE: 'intermediate',
  ADVANCED: 'advanced',
  EXPERT: 'expert',
};

export const EXPERIENCE_LEVELS = {
  ENTRY: 'entry',
  JUNIOR: 'junior',
  MID: 'mid',
  SENIOR: 'senior',
  LEAD: 'lead',
  EXECUTIVE: 'executive',
};

export const EDUCATION_LEVELS = {
  HIGH_SCHOOL: 'high_school',
  ASSOCIATE: 'associate',
  BACHELORS: 'bachelors',
  MASTERS: 'masters',
  DOCTORATE: 'doctorate',
  CERTIFICATE: 'certificate',
};

export const INDUSTRIES = [
  'Technology',
  'Finance',
  'Healthcare',
  'Education',
  'Manufacturing',
  'Retail',
  'Media',
  'Consulting',
  'Real Estate',
  'Transportation',
  'Energy',
  'Nonprofit',
];

export const JOB_TYPES = {
  FULL_TIME: 'full_time',
  PART_TIME: 'part_time',
  CONTRACT: 'contract',
  INTERNSHIP: 'internship',
  REMOTE: 'remote',
  HYBRID: 'hybrid',
};

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    VERIFY: '/auth/verify',
  },
  PROFILE: {
    BASE: '/profile',
    EXPERIENCE: '/profile/experience',
    EDUCATION: '/profile/education',
    SKILLS: '/profile/skills',
  },
  CVS: {
    BASE: '/cvs',
    GENERATE: '/cvs/generate',
    DOWNLOAD: (id, format) => `/cvs/${id}/download/${format}`,
  },
  AI: {
    ANALYZE: '/ai/analyze',
    SUGGEST: '/ai/suggest',
    IMPROVE: '/ai/improve',
  },
};

export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your internet connection.',
  UNAUTHORIZED: 'Your session has expired. Please login again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  NOT_FOUND: 'Resource not found.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  PROFILE_SAVE_ERROR: 'Failed to save profile. Please try again.',
  CV_GENERATION_ERROR: 'Failed to generate CV. Please try again.',
  JOB_ANALYSIS_ERROR: 'Failed to analyze job description. Please try again.',
};