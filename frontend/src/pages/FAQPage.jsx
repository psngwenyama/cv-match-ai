import React, { useState } from 'react';
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';

const FAQPage = () => {
  const [openIndex, setOpenIndex] = useState(null);

  const faqs = [
    {
      question: "How does CV-Match AI work?",
      answer: "CV-Match AI uses advanced AI technology to analyze job descriptions and match them with your master profile. You simply create your complete profile once, then paste any job description. Our AI extracts key requirements and automatically tailors your CV to highlight the most relevant skills and experiences for that specific role."
    },
    {
      question: "Is my data secure?",
      answer: "Yes, we take data security seriously. All personal information is encrypted both in transit and at rest. We use industry-standard security practices including JWT authentication, HTTPS encryption, and secure database storage. Your data is never shared with third parties without your explicit consent."
    },
    {
      question: "Will my CV pass ATS (Applicant Tracking Systems)?",
      answer: "Our AI is specifically designed to optimize your CV for ATS systems. The system analyzes job descriptions for relevant keywords and structures your CV using ATS-friendly formatting. However, no system can guarantee 100% ATS compatibility as different systems have varying algorithms, but our users report significantly improved pass rates."
    },
    {
      question: "Can I edit the AI-generated CV?",
      answer: "Absolutely! We encourage users to review and edit their AI-generated CVs. The system provides a preview where you can make manual adjustments before downloading or saving. You have full control over the final output."
    },
    {
      question: "What file formats can I export my CV in?",
      answer: "You can export your CV in both PDF and DOCX formats. PDF is ideal for direct applications, while DOCX allows for further editing in Microsoft Word or Google Docs if needed."
    },
    {
      question: "How many CVs can I generate?",
      answer: "There's no limit to the number of CVs you can generate. You can create tailored CVs for as many job applications as you want. All your generated CVs are saved in your history for easy access and future reference."
    },
    {
      question: "Is CV-Match AI free?",
      answer: "We offer a free tier that allows you to generate up to 5 CVs. For unlimited access and advanced features, we have affordable subscription plans. Check our pricing page for detailed information."
    },
    {
      question: "What AI technology do you use?",
      answer: "We use state-of-the-art Large Language Models (LLMs) including OpenAI GPT-4 and Claude AI. Our system uses advanced prompt engineering to ensure accurate job matching and content generation while maintaining factual accuracy from your profile."
    },
    {
      question: "Do you support multiple languages?",
      answer: "Currently, CV-Match AI supports English language job descriptions and CVs. We plan to add support for additional languages in future updates."
    },
    {
      question: "How long does it take to generate a CV?",
      answer: "CV generation typically takes less than 10 seconds. Our asynchronous processing ensures you're not waiting, and you can continue using the platform while your CV is being generated."
    }
  ];

  const toggleFAQ = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Frequently Asked Questions</h1>
        <p className="text-xl text-gray-600">
          Find answers to common questions about CV-Match AI
        </p>
      </div>

      {/* FAQ List */}
      <div className="space-y-4">
        {faqs.map((faq, index) => (
          <div key={index} className="border border-gray-200 rounded-lg overflow-hidden">
            <button
              onClick={() => toggleFAQ(index)}
              className="w-full flex justify-between items-center p-6 text-left bg-white hover:bg-gray-50 transition-colors"
            >
              <span className="text-lg font-semibold text-gray-900">{faq.question}</span>
              {openIndex === index ? (
                <ChevronUpIcon className="h-5 w-5 text-gray-500" />
              ) : (
                <ChevronDownIcon className="h-5 w-5 text-gray-500" />
              )}
            </button>
            <div
              className={`transition-all duration-300 ease-in-out ${
                openIndex === index ? 'block' : 'hidden'
              }`}
            >
              <div className="p-6 pt-0 bg-gray-50 border-t border-gray-100">
                <p className="text-gray-600">{faq.answer}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Still have questions */}
      <div className="mt-12 text-center bg-gray-50 rounded-2xl p-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Still have questions?</h2>
        <p className="text-gray-600 mb-6">
          Can't find the answer you're looking for? Please contact our support team.
        </p>
        <a
          href="/contact"
          className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          Contact Us
        </a>
      </div>
    </div>
  );
};

export default FAQPage;