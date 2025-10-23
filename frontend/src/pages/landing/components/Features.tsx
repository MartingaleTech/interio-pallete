import { Briefcase, Users, Calendar, FileText, Image, CreditCard, Shield, Zap } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'

const features = [
  {
    icon: Briefcase,
    title: 'Project Management',
    description: 'Organize and track all your interior design projects in one place. Monitor progress, budgets, and timelines effortlessly.'
  },
  {
    icon: Users,
    title: 'Client Portal',
    description: 'Give your clients a dedicated portal to view project updates, designs, and invoices. Keep them engaged throughout the journey.'
  },
  {
    icon: Calendar,
    title: 'Smart Scheduling',
    description: 'Coordinate site visits, client meetings, and team schedules with an integrated calendar system.'
  },
  {
    icon: FileText,
    title: 'Invoice Management',
    description: 'Generate professional invoices, track payments, and manage billing seamlessly. Get paid faster.'
  },
  {
    icon: Image,
    title: 'Design Gallery',
    description: 'Upload and organize design files, mood boards, and project photos. Share them instantly with clients.'
  },
  {
    icon: Users,
    title: 'Team Collaboration',
    description: 'Assign team members to projects, define roles, and collaborate in real-time. Everyone stays on the same page.'
  },
  {
    icon: Shield,
    title: 'Multi-tenant Security',
    description: 'Enterprise-grade security with complete data isolation. Your business data stays private and secure.'
  },
  {
    icon: Zap,
    title: 'Real-time Updates',
    description: 'Instant notifications and updates keep everyone informed. No more back-and-forth emails.'
  }
]

export function Features() {
  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            Everything You Need to Run Your Design Business
          </h2>
          <p className="text-xl text-gray-600">
            Powerful features designed specifically for interior designers and their clients
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <Card key={index} className="border-2 hover:border-purple-200 hover:shadow-lg transition-all duration-300">
                <CardContent className="p-6 space-y-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-100 to-blue-100 rounded-xl flex items-center justify-center">
                    <Icon className="w-6 h-6 text-purple-600" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900">{feature.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </section>
  )
}
