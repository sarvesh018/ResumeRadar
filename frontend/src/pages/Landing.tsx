import { Link } from 'react-router-dom';
import Button from '../components/shared/Button';

export default function Landing() {
  return (
    <div className="min-h-screen bg-linear-to-br from-indigo-50 to-white">
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl font-extrabold text-gray-900 mb-6">
          Optimize Your Resume.<br />
          <span className="text-indigo-600">Track Your Applications.</span>
        </h1>
        <p className="text-xl text-gray-600 mb-10">
          ResumeRadar matches your resume against job descriptions, helps you track every application, and shows what’s working.
        </p>
        <div className="flex justify-center gap-4">
          <Link to="/register">
            <Button variant="primary" className="px-8 py-3 text-lg">Get Started</Button>
          </Link>
          <Link to="/login">
            <Button variant="outline" className="px-8 py-3 text-lg">Login</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}