import { Button } from '@/components/ui/button'
import { ArrowRight, Play } from 'lucide-react'

export function Hero() {
  return (
    <section className="relative bg-gradient-to-br from-purple-50 via-blue-50 to-purple-50 pt-32 pb-20 overflow-hidden">
      <div className="absolute inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] -z-10" />
      
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <div className="inline-block">
              <span className="bg-purple-100 text-purple-700 px-4 py-2 rounded-full text-sm font-medium">
                🎨 Transform Your Interior Design Business
              </span>
            </div>
            
            <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
              Connect Designers with
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-600"> Homeowners</span>
            </h1>
            
            <p className="text-xl text-gray-600 leading-relaxed">
              Streamline your interior design projects with our all-in-one platform. 
              Manage clients, collaborate with teams, and deliver stunning results.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <Button 
                size="lg" 
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-8 py-6 text-lg"
                onClick={() => window.location.href = '/login'}
              >
                Get Started Free
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              
              <Button 
                size="lg" 
                variant="outline" 
                className="px-8 py-6 text-lg border-2"
              >
                <Play className="mr-2 h-5 w-5" />
                Watch Demo
              </Button>
            </div>
            
            <div className="flex items-center gap-8 pt-4">
              <div className="flex -space-x-2">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-blue-400 border-2 border-white"
                  />
                ))}
              </div>
              <div>
                <p className="text-sm text-gray-600">
                  <span className="font-bold text-gray-900">500+</span> design firms trust us
                </p>
              </div>
            </div>
          </div>
          
          <div className="relative">
            <div className="relative rounded-2xl overflow-hidden shadow-2xl bg-white p-4">
              <div className="aspect-video bg-gradient-to-br from-purple-100 to-blue-100 rounded-lg flex items-center justify-center">
                <div className="text-center space-y-4">
                  <div className="w-20 h-20 mx-auto bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center">
                    <Play className="w-10 h-10 text-white" />
                  </div>
                  <p className="text-gray-600 font-medium">Product Demo</p>
                </div>
              </div>
            </div>
            
            <div className="absolute -top-4 -right-4 w-24 h-24 bg-yellow-400 rounded-full blur-3xl opacity-50" />
            <div className="absolute -bottom-4 -left-4 w-32 h-32 bg-purple-400 rounded-full blur-3xl opacity-50" />
          </div>
        </div>
      </div>
    </section>
  )
}
