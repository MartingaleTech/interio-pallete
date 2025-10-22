import { useState } from 'react'
import { Building2, Phone, Mail } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { authService } from '../../../services/authService'
import { useAuth } from '../../../state/AuthContext'

export function LoginForm() {
  const { login } = useAuth()
  const [loginMethod, setLoginMethod] = useState<'email' | 'phone'>('email')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [phone, setPhone] = useState('')
  const [otp, setOtp] = useState('')
  const [otpSent, setOtpSent] = useState(false)
  const [mockOtp, setMockOtp] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleEmailLogin = async () => {
    setIsLoading(true)
    try {
      const data = await authService.login(email, password)
      login(data.token, data.user)
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to login')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRequestOtp = async () => {
    setIsLoading(true)
    try {
      const data = await authService.requestOtp(phone)
      setMockOtp(data.otp)
      setOtpSent(true)
      alert(`Mock OTP sent: ${data.otp}`)
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to send OTP')
    } finally {
      setIsLoading(false)
    }
  }

  const handleVerifyOtp = async () => {
    setIsLoading(true)
    try {
      const data = await authService.verifyOtp(phone, otp)
      login(data.token, data.user)
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to verify OTP')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-2 text-center">
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center mb-4">
            <Building2 className="w-8 h-8 text-white" />
          </div>
          <CardTitle className="text-3xl font-bold">Interio Palette</CardTitle>
          <CardDescription className="text-base">
            Connect interior designers with homeowners
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Tabs defaultValue="email" className="w-full" onValueChange={(v) => setLoginMethod(v as 'email' | 'phone')}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="email">
                <Mail className="w-4 h-4 mr-2" />
                Email
              </TabsTrigger>
              <TabsTrigger value="phone">
                <Phone className="w-4 h-4 mr-2" />
                Phone
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="email" className="space-y-4 mt-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Email</label>
                <Input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Password</label>
                <Input
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <p className="text-xs text-gray-500">
                Demo: admin@designerconnect.com / admin123
              </p>
              <Button 
                onClick={handleEmailLogin} 
                className="w-full" 
                disabled={!email || !password || isLoading}
              >
                {isLoading ? 'Logging in...' : 'Login'}
              </Button>
            </TabsContent>
            
            <TabsContent value="phone" className="space-y-4 mt-4">
              {!otpSent ? (
                <>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Phone Number</label>
                    <Input
                      type="tel"
                      placeholder="Enter your phone number"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                    />
                    <p className="text-xs text-gray-500">
                      Demo phones: 9999999999 (admin), or any org member phone
                    </p>
                  </div>
                  <Button 
                    onClick={handleRequestOtp} 
                    className="w-full" 
                    disabled={!phone || isLoading}
                  >
                    {isLoading ? 'Sending...' : 'Send OTP'}
                  </Button>
                </>
              ) : (
                <>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Enter OTP</label>
                    <Input
                      type="text"
                      placeholder="Enter 6-digit OTP"
                      value={otp}
                      onChange={(e) => setOtp(e.target.value)}
                      maxLength={6}
                    />
                    {mockOtp && (
                      <p className="text-xs text-green-600 font-medium">
                        Mock OTP: {mockOtp}
                      </p>
                    )}
                  </div>
                  <Button 
                    onClick={handleVerifyOtp} 
                    className="w-full" 
                    disabled={!otp || isLoading}
                  >
                    {isLoading ? 'Verifying...' : 'Verify & Login'}
                  </Button>
                  <Button 
                    onClick={() => { setOtpSent(false); setOtp(''); setMockOtp(''); }} 
                    variant="outline" 
                    className="w-full"
                    disabled={isLoading}
                  >
                    Change Phone Number
                  </Button>
                </>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}
