import { Card, CardContent } from '@/components/ui/card'
import { Star } from 'lucide-react'

const testimonials = [
  {
    name: 'Priya Sharma',
    role: 'Founder, Elegant Interiors',
    location: 'Mumbai',
    content: 'Interio Palette has transformed how we manage our projects. Our clients love the transparency and we\'ve reduced project delays by 40%.',
    rating: 5,
    image: '👩‍💼'
  },
  {
    name: 'Rajesh Kumar',
    role: 'Lead Designer, Modern Spaces',
    location: 'Bangalore',
    content: 'The client portal is a game-changer. Our homeowners can track everything in real-time, which has significantly improved our customer satisfaction scores.',
    rating: 5,
    image: '👨‍💼'
  },
  {
    name: 'Anita Desai',
    role: 'Owner, Luxe Living Designs',
    location: 'Delhi',
    content: 'We\'ve been using Interio Palette for 6 months and it\'s been incredible. The invoice management alone has saved us countless hours every month.',
    rating: 5,
    image: '👩'
  },
  {
    name: 'Vikram Patel',
    role: 'Creative Director, Studio V',
    location: 'Pune',
    content: 'Finally, a platform built specifically for interior designers! The design gallery feature makes it so easy to share mood boards and concepts with clients.',
    rating: 5,
    image: '👨'
  },
  {
    name: 'Meera Reddy',
    role: 'Principal Designer, Artisan Homes',
    location: 'Hyderabad',
    content: 'The team collaboration features are excellent. Everyone on my team knows exactly what they need to do and when. Highly recommended!',
    rating: 5,
    image: '👩‍🎨'
  },
  {
    name: 'Arjun Malhotra',
    role: 'Managing Partner, Elite Interiors',
    location: 'Chennai',
    content: 'Best investment we\'ve made for our business. The ROI has been phenomenal - we\'re handling 3x more projects with the same team size.',
    rating: 5,
    image: '👨‍💻'
  }
]

export function Testimonials() {
  return (
    <section className="py-20 bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            Loved by Design Professionals
          </h2>
          <p className="text-xl text-gray-600">
            See what interior designers across India are saying about Interio Palette
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <Card key={index} className="border-2 hover:shadow-xl transition-shadow duration-300">
              <CardContent className="p-6 space-y-4">
                <div className="flex gap-1">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                
                <p className="text-gray-700 leading-relaxed italic">
                  "{testimonial.content}"
                </p>
                
                <div className="flex items-center gap-3 pt-4 border-t">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-blue-400 rounded-full flex items-center justify-center text-2xl">
                    {testimonial.image}
                  </div>
                  <div>
                    <p className="font-bold text-gray-900">{testimonial.name}</p>
                    <p className="text-sm text-gray-600">{testimonial.role}</p>
                    <p className="text-xs text-gray-500">{testimonial.location}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
