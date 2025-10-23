import { UserPlus, FolderPlus, Users2, CheckCircle } from 'lucide-react'

const steps = [
  {
    icon: UserPlus,
    title: 'Sign Up & Setup',
    description: 'Create your organization account in minutes. Add your team members and customize your workspace.'
  },
  {
    icon: FolderPlus,
    title: 'Create Projects',
    description: 'Add your clients and create projects. Set budgets, timelines, and assign team members.'
  },
  {
    icon: Users2,
    title: 'Collaborate & Execute',
    description: 'Upload designs, schedule meetings, and keep everyone updated. Your clients can track progress in real-time.'
  },
  {
    icon: CheckCircle,
    title: 'Deliver & Invoice',
    description: 'Complete projects with confidence. Generate invoices and get paid faster with integrated billing.'
  }
]

export function HowItWorks() {
  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-purple-50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            How It Works
          </h2>
          <p className="text-xl text-gray-600">
            Get started in four simple steps and transform your design workflow
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => {
            const Icon = step.icon
            return (
              <div key={index} className="relative">
                <div className="text-center space-y-4">
                  <div className="relative inline-block">
                    <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                      <Icon className="w-10 h-10 text-white" />
                    </div>
                    <div className="absolute -top-2 -right-2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-md">
                      <span className="text-sm font-bold text-purple-600">{index + 1}</span>
                    </div>
                  </div>
                  
                  <h3 className="text-xl font-bold text-gray-900">{step.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{step.description}</p>
                </div>
                
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-10 left-full w-full h-0.5 bg-gradient-to-r from-purple-300 to-blue-300 -translate-x-1/2" />
                )}
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
