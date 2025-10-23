import { Header } from './landing/components/Header'
import { Footer } from './landing/components/Footer'
import { Button } from '@/components/ui/button'
import { Target, Eye, Heart, Users } from 'lucide-react'

export function About() {
  const values = [
    {
      icon: Target,
      title: 'Mission Driven',
      description: 'To empower interior designers with technology that simplifies their workflow and enhances client relationships.'
    },
    {
      icon: Eye,
      title: 'Visionary',
      description: 'We envision a world where every interior designer has access to professional-grade tools, regardless of their business size.'
    },
    {
      icon: Heart,
      title: 'Customer First',
      description: 'Every feature we build is driven by feedback from real designers solving real problems in their daily work.'
    },
    {
      icon: Users,
      title: 'Community Focused',
      description: 'We believe in building a community of designers who support and learn from each other.'
    }
  ]

  const team = [
    { name: 'Priya Sharma', role: 'CEO & Founder', emoji: '👩‍💼' },
    { name: 'Rajesh Kumar', role: 'CTO', emoji: '👨‍💻' },
    { name: 'Anita Desai', role: 'Head of Design', emoji: '👩‍🎨' },
    { name: 'Vikram Patel', role: 'Head of Product', emoji: '👨‍💼' }
  ]

  return (
    <div className="min-h-screen">
      <Header />
      
      <main className="pt-16">
        <section className="py-20 bg-gradient-to-br from-purple-50 to-blue-50">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto text-center space-y-6">
              <h1 className="text-5xl lg:text-6xl font-bold text-gray-900">
                About Interio Palette
              </h1>
              <p className="text-xl text-gray-600 leading-relaxed">
                We're on a mission to transform how interior designers work with their clients. 
                Founded in 2024, Interio Palette was born from the frustration of managing design 
                projects across multiple tools and platforms.
              </p>
            </div>
          </div>
        </section>

        <section className="py-20 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto space-y-8">
              <h2 className="text-4xl font-bold text-gray-900 text-center mb-12">
                Our Story
              </h2>
              
              <div className="prose prose-lg max-w-none text-gray-600 space-y-6">
                <p>
                  Interio Palette was founded by a team of designers and technologists who 
                  experienced firsthand the challenges of managing interior design projects. 
                  We saw talented designers spending more time on administrative tasks than 
                  on what they love - creating beautiful spaces.
                </p>
                
                <p>
                  We built Interio Palette to solve this problem. Our platform brings together 
                  project management, client communication, team collaboration, and billing into 
                  one seamless experience. No more juggling between spreadsheets, email threads, 
                  and multiple apps.
                </p>
                
                <p>
                  Today, we're proud to serve over 500 design firms across India, helping them 
                  manage thousands of projects and deliver exceptional experiences to their clients. 
                  But we're just getting started.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="py-20 bg-gray-50">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-4xl font-bold text-gray-900 text-center mb-12">
              Our Values
            </h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
              {values.map((value, index) => {
                const Icon = value.icon
                return (
                  <div key={index} className="text-center space-y-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center mx-auto">
                      <Icon className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-xl font-bold text-gray-900">{value.title}</h3>
                    <p className="text-gray-600 leading-relaxed">{value.description}</p>
                  </div>
                )
              })}
            </div>
          </div>
        </section>

        <section className="py-20 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                Meet Our Team
              </h2>
              <p className="text-xl text-gray-600">
                The people behind Interio Palette
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-5xl mx-auto">
              {team.map((member, index) => (
                <div key={index} className="text-center space-y-4">
                  <div className="w-32 h-32 bg-gradient-to-br from-purple-400 to-blue-400 rounded-full flex items-center justify-center mx-auto text-6xl">
                    {member.emoji}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">{member.name}</h3>
                    <p className="text-gray-600">{member.role}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="py-20 bg-gradient-to-br from-purple-600 to-blue-600">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto text-center space-y-8">
              <h2 className="text-4xl font-bold text-white">
                Join Us on This Journey
              </h2>
              <p className="text-xl text-purple-100">
                We're always looking for talented people who share our passion for 
                design and technology. Check out our open positions.
              </p>
              <Button 
                size="lg" 
                className="bg-white text-purple-600 hover:bg-gray-100 px-8 py-6 text-lg"
              >
                View Careers
              </Button>
            </div>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  )
}
