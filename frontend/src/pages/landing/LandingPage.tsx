import { Header } from './components/Header'
import { Hero } from './components/Hero'
import { Features } from './components/Features'
import { HowItWorks } from './components/HowItWorks'
import { Pricing } from './components/Pricing'
import { Testimonials } from './components/Testimonials'
import { FAQ } from './components/FAQ'
import { CTA } from './components/CTA'
import { Footer } from './components/Footer'

export function LandingPage() {
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <Hero />
        <div id="features" className="scroll-mt-20">
          <Features />
        </div>
        <HowItWorks />
        <div id="pricing" className="scroll-mt-20">
          <Pricing />
        </div>
        <Testimonials />
        <FAQ />
        <CTA />
      </main>
      <Footer />
    </div>
  )
}
