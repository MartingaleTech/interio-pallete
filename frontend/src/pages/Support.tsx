import { Header } from './landing/components/Header'
import { Footer } from './landing/components/Footer'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { Book, MessageCircle, Video, FileText, Search, HelpCircle } from 'lucide-react'

export function Support() {
  const resources = [
    {
      icon: Book,
      title: 'Documentation',
      description: 'Comprehensive guides and tutorials to help you get started',
      link: '#'
    },
    {
      icon: Video,
      title: 'Video Tutorials',
      description: 'Step-by-step video guides for all features',
      link: '#'
    },
    {
      icon: FileText,
      title: 'API Documentation',
      description: 'Technical documentation for developers',
      link: '#'
    },
    {
      icon: MessageCircle,
      title: 'Community Forum',
      description: 'Connect with other designers and share tips',
      link: '#'
    }
  ]

  const popularTopics = [
    'Getting Started with Interio Palette',
    'How to Add Team Members',
    'Creating Your First Project',
    'Inviting Clients to the Portal',
    'Managing Invoices and Payments',
    'Uploading Design Files',
    'Setting Up Calendar Events',
    'Understanding Pricing Plans',
    'Data Security and Privacy',
    'Integrating with Other Tools'
  ]

  return (
    <div className="min-h-screen">
      <Header />
      
      <main className="pt-16">
        <section className="py-20 bg-gradient-to-br from-purple-50 to-blue-50">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto text-center space-y-6">
              <h1 className="text-5xl lg:text-6xl font-bold text-gray-900">
                How Can We Help?
              </h1>
              <p className="text-xl text-gray-600">
                Search our knowledge base or browse popular topics below
              </p>
              
              <div className="max-w-2xl mx-auto">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <Input
                    placeholder="Search for help articles..."
                    className="pl-12 py-6 text-lg"
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="py-20 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-4xl font-bold text-gray-900 text-center mb-12">
              Support Resources
            </h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
              {resources.map((resource, index) => {
                const Icon = resource.icon
                return (
                  <Card key={index} className="border-2 hover:border-purple-200 hover:shadow-lg transition-all cursor-pointer">
                    <CardContent className="p-6 text-center space-y-4">
                      <div className="w-16 h-16 bg-gradient-to-br from-purple-100 to-blue-100 rounded-2xl flex items-center justify-center mx-auto">
                        <Icon className="w-8 h-8 text-purple-600" />
                      </div>
                      <h3 className="text-xl font-bold text-gray-900">{resource.title}</h3>
                      <p className="text-gray-600">{resource.description}</p>
                      <Button variant="link" className="text-purple-600">
                        Learn More →
                      </Button>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </div>
        </section>

        <section className="py-20 bg-gray-50">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-4xl font-bold text-gray-900 text-center mb-12">
                Popular Topics
              </h2>
              
              <div className="grid md:grid-cols-2 gap-4">
                {popularTopics.map((topic, index) => (
                  <Card key={index} className="border-2 hover:border-purple-200 hover:shadow-md transition-all cursor-pointer">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-3">
                        <HelpCircle className="w-5 h-5 text-purple-600 flex-shrink-0" />
                        <span className="text-gray-700 font-medium">{topic}</span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="py-20 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto">
              <Card className="border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-blue-50">
                <CardContent className="p-12 text-center space-y-6">
                  <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center mx-auto">
                    <MessageCircle className="w-10 h-10 text-white" />
                  </div>
                  
                  <h2 className="text-3xl font-bold text-gray-900">
                    Still Need Help?
                  </h2>
                  
                  <p className="text-xl text-gray-600">
                    Our support team is here to help. Get in touch and we'll respond as soon as possible.
                  </p>
                  
                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Button 
                      size="lg"
                      className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                    >
                      Contact Support
                    </Button>
                    
                    <Button 
                      size="lg"
                      variant="outline"
                      className="border-2"
                    >
                      Schedule a Call
                    </Button>
                  </div>
                  
                  <div className="pt-6 border-t border-purple-200">
                    <p className="text-sm text-gray-600">
                      <strong>Response Times:</strong> Starter (24 hours) • Professional (12 hours) • Enterprise (2 hours)
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  )
}
