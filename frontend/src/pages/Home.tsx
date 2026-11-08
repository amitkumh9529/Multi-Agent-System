import { Link } from 'react-router-dom';

export default function Home() {
  const sections = [
    { name: 'Teams', href: '/teams', icon: '👥', description: 'Manage your AI teams' },
    { name: 'Agents', href: '/agents', icon: '🤖', description: 'Configure AI agents' },
    { name: 'Prompts', href: '/prompts', icon: '📝', description: 'Manage prompt templates' },
    { name: 'Knowledge Bases', href: '/kb', icon: '📚', description: 'Manage your knowledge bases' },
    { name: 'Chat', href: '/chat', icon: '💬', description: 'Start a new conversation' }
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 bg-gray-50 h-full">
      <div className="max-w-4xl w-full space-y-8">
        <div className="text-center">
          <h1 className="text-5xl font-extrabold text-gray-900 tracking-tight sm:text-6xl">
            Welcome to <span className="text-primary-600">MAS Platform</span>
          </h1>
          <p className="mt-4 text-xl text-gray-500 max-w-2xl mx-auto">
            Get started by exploring the available modules. Start a chat, manage your agents, or configure knowledge bases.
          </p>
        </div>
        
        <div className="mt-12 flex flex-wrap justify-center gap-6 py-8">
          {sections.map((section) => (
            <Link
              key={section.name}
              to={section.href}
              className="relative w-64 group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary-500 rounded-2xl shadow-sm hover:shadow-md transition-all duration-200 border border-gray-100 flex flex-col items-center text-center"
            >
              <span className="rounded-lg inline-flex p-3 bg-primary-50 text-primary-700 ring-4 ring-white mb-4">
                <span className="text-3xl">{section.icon}</span>
              </span>
              <h3 className="text-lg font-medium text-gray-900">
                {section.name}
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                {section.description}
              </p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
