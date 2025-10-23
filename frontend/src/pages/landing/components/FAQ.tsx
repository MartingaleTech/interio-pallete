import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'

const faqs = [
  {
    question: 'How does the free trial work?',
    answer: 'You get full access to all features for 14 days, no credit card required. You can cancel anytime during the trial period without any charges.'
  },
  {
    question: 'Can I switch plans later?',
    answer: 'Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately and we\'ll prorate any charges or credits.'
  },
  {
    question: 'Is my data secure?',
    answer: 'Absolutely. We use enterprise-grade encryption, regular backups, and complete data isolation between organizations. Your data is stored in secure data centers with 99.9% uptime.'
  },
  {
    question: 'How many team members can I add?',
    answer: 'It depends on your plan. Starter allows 5 members, Professional allows 20, and Enterprise has unlimited team members. You can always upgrade as your team grows.'
  },
  {
    question: 'Do clients need to create accounts?',
    answer: 'Yes, but it\'s super simple. When you add a client, they receive an invitation to create their account. They can then access their dedicated portal to view project updates.'
  },
  {
    question: 'Can I customize invoices with my branding?',
    answer: 'Professional and Enterprise plans include custom branding options for invoices. You can add your logo, colors, and company details.'
  },
  {
    question: 'What payment methods do you accept?',
    answer: 'We accept all major credit/debit cards, UPI, net banking, and digital wallets. All payments are processed securely through our payment gateway.'
  },
  {
    question: 'Is there a setup fee?',
    answer: 'No setup fees! You only pay the monthly or annual subscription fee based on your chosen plan.'
  },
  {
    question: 'Can I export my data?',
    answer: 'Yes, you can export all your data at any time in standard formats (CSV, PDF). You own your data and can take it with you if you decide to leave.'
  },
  {
    question: 'What kind of support do you provide?',
    answer: 'Starter plans get email support, Professional plans get priority email and chat support, and Enterprise plans get 24/7 phone support with a dedicated account manager.'
  }
]

export function FAQ() {
  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-xl text-gray-600">
            Got questions? We've got answers. Can't find what you're looking for? Contact our support team.
          </p>
        </div>
        
        <div className="max-w-3xl mx-auto">
          <Accordion type="single" collapsible className="space-y-4">
            {faqs.map((faq, index) => (
              <AccordionItem 
                key={index} 
                value={`item-${index}`}
                className="border-2 rounded-lg px-6"
              >
                <AccordionTrigger className="text-left text-lg font-semibold hover:no-underline">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-gray-600 leading-relaxed">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </div>
    </section>
  )
}
