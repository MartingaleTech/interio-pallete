import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Building2, Menu, X } from 'lucide-react'
import { Link } from 'react-router-dom'

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const navigation = [
    { name: 'Features', href: '#features' },
    { name: 'Pricing', href: '#pricing' },
    { name: 'About', href: '/about' },
    { name: 'Contact', href: '/contact' },
    { name: 'Support', href: '/support' }
  ]

  return (
    <header className="fixed top-0 left-0 right-0 bg-white/95 backdrop-blur-sm border-b border-gray-200 z-50">
      <nav className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
              <Building2 className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">Interio Palette</span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            {navigation.map((item) => (
              item.href.startsWith('#') ? (
                <a
                  key={item.name}
                  href={item.href}
                  className="text-gray-600 hover:text-purple-600 font-medium transition-colors"
                >
                  {item.name}
                </a>
              ) : (
                <Link
                  key={item.name}
                  to={item.href}
                  className="text-gray-600 hover:text-purple-600 font-medium transition-colors"
                >
                  {item.name}
                </Link>
              )
            ))}
          </div>

          <div className="hidden md:flex items-center gap-4">
            <Button variant="ghost" onClick={() => window.location.href = '/login'}>
              Sign In
            </Button>
            <Button 
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
              onClick={() => window.location.href = '/login'}
            >
              Get Started
            </Button>
          </div>

          <button
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <X className="w-6 h-6 text-gray-900" />
            ) : (
              <Menu className="w-6 h-6 text-gray-900" />
            )}
          </button>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden py-4 space-y-4 border-t">
            {navigation.map((item) => (
              item.href.startsWith('#') ? (
                <a
                  key={item.name}
                  href={item.href}
                  className="block text-gray-600 hover:text-purple-600 font-medium"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.name}
                </a>
              ) : (
                <Link
                  key={item.name}
                  to={item.href}
                  className="block text-gray-600 hover:text-purple-600 font-medium"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.name}
                </Link>
              )
            ))}
            <div className="flex flex-col gap-2 pt-4">
              <Button variant="outline" className="w-full" onClick={() => window.location.href = '/login'}>
                Sign In
              </Button>
              <Button 
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600"
                onClick={() => window.location.href = '/login'}
              >
                Get Started
              </Button>
            </div>
          </div>
        )}
      </nav>
    </header>
  )
}
