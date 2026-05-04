import React from 'react';
import { Link } from 'react-router-dom';
import { 
  DocumentTextIcon, 
  SparklesIcon, 
  ClockIcon,
  CheckCircleIcon,
  ArrowTrendingUpIcon,
  UserGroupIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline';

const HomePage = () => {
  const features = [
    {
      icon: SparklesIcon,
      title: 'AI-Powered Matching',
      description: 'Our AI analyzes job descriptions and tailors your CV to highlight the most relevant skills and experiences.'
    },
    {
      icon: ClockIcon,
      title: 'Save Time',
      description: 'Stop manually customizing CVs for each application. Generate tailored CVs in seconds.'
    },
    {
      icon: CheckCircleIcon,
      title: 'ATS Optimized',
      description: 'Ensure your CV passes Applicant Tracking Systems with keyword-optimized content.'
    },
    {
      icon: ArrowTrendingUpIcon,
      title: 'Increase Interview Rate',
      description: 'Users report up to 40% more interview calls with our AI-tailored CVs.'
    },
    {
      icon: UserGroupIcon,
      title: 'Career Switch Support',
      description: 'Perfect for students and professionals changing careers who need to highlight transferable skills.'
    },
    {
      icon: DocumentTextIcon,
      title: 'Multiple Templates',
      description: 'Choose from professional, modern, or creative templates for different industries.'
    }
  ];

  const stats = [
    { value: '10,000+', label: 'CVs Generated' },
    { value: '95%', label: 'User Satisfaction' },
    { value: '60%', label: 'CVs Generated' },
    { value: '5min', label: 'Average Time' }
  ];

  return (
    <div className="space-y-16">
      {/* Hero Section with White Background - exactly like PDF */}
      <section className="relative bg-white overflow-hidden pt-16 pb-32">
        {/* Left Image - positioned closer to text */}
        <div className="absolute left-0 top-1/2 transform -translate-y-1/2 z-10" style={{ left: '5%' }}>
          <img 
            src="/assets/3.png" 
            alt="CV illustration" 
            className="w-56 md:w-72 lg:w-80 h-auto object-contain"
          />
        </div>
        
        {/* Right Image - positioned closer to text */}
        <div className="absolute right-0 top-1/2 transform -translate-y-1/2 z-10" style={{ right: '5%' }}>
          <img 
            src="/assets/4.png" 
            alt="CV illustration" 
            className="w-56 md:w-72 lg:w-80 h-auto object-contain"
          />
        </div>
        
        {/* Center Content */}
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center z-20">
          <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-gray-900 mb-8">
            Let's create your CV
          </h1>
          
          {/* Down Arrow pointing to Start Here button */}
          <div className="flex justify-center mb-6 animate-bounce">
            <ArrowDownIcon className="h-8 w-8 text-blue-600" />
          </div>
          
          {/* Start Here Button */}
          <div className="flex flex-col items-center gap-4">
            <Link
              to="/register"
              className="bg-blue-600 text-white px-12 py-4 rounded-xl text-lg font-semibold hover:bg-blue-700 transition-colors shadow-md inline-block"
            >
              Start Here
            </Link>
            
            {/* Watch Demo below Start Here */}
            <Link
              to="/demo"
              className="text-gray-600 hover:text-gray-900 text-base font-medium transition-colors"
            >
              Watch Demo
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Section - floating cards */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 mt-10 relative z-30">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
          {stats.map((stat, index) => (
            <div key={index} className="bg-white rounded-2xl shadow-lg p-6 text-center border border-gray-100">
              <div className="text-3xl md:text-4xl font-bold text-blue-600 mb-2">
                {stat.value}
              </div>
              <div className="text-gray-600 text-sm md:text-base">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
          Why Choose CV-Match AI?
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="bg-white rounded-2xl p-6 shadow-md hover:shadow-xl transition-shadow border border-gray-100">
              <feature.icon className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2 text-gray-900">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">1</span>
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900">Create Profile</h3>
              <p className="text-gray-600">Add all your skills, experiences, and achievements to your master profile.</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">2</span>
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900">Paste Job Description</h3>
              <p className="text-gray-600">Copy and paste any job description you want to apply for.</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">3</span>
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900">Generate CV</h3>
              <p className="text-gray-600">Get a perfectly tailored CV optimized for that specific job.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl p-12 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">Ready to Land Your Dream Job?</h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of job seekers who have improved their applications with CV-Match AI.
          </p>
          <Link
            to="/register"
            className="inline-block bg-white text-blue-600 px-10 py-4 rounded-xl text-lg font-semibold hover:bg-gray-100 transition-colors shadow-lg"
          >
            Create Free Account
          </Link>
        </div>
      </section>
    </div>
  );
};

export default HomePage;