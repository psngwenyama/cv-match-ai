// eslint-disable-next-line no-unused-vars
import React from 'react';
import { ExclamationCircleIcon } from '@heroicons/react/24/outline';

const ErrorMessage = ({ message, onRetry }) => {
  return (
    <div className="rounded-lg bg-red-50 p-4">
      <div className="flex items-center">
        <ExclamationCircleIcon className="h-5 w-5 text-red-400" />
        <div className="ml-3">
          <p className="text-sm text-red-800">{message}</p>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="ml-auto text-sm font-medium text-red-600 hover:text-red-500"
          >
            Retry
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage;