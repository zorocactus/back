import { useState } from "react";
import { User, EyeOff, Eye, Facebook } from "lucide-react";

export default function App() {
  const [firstName, setFirstName] = useState("")
  const [lastName, setLastName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [errors, setErrors] = useState({})

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [accountType, setAccountType] = useState("patient");

  function handleSubmit() {
    const newErrors = {}
    if (!firstName.trim())       newErrors["firstName"] = true
    if (!lastName.trim())        newErrors["lastName"] = true
    if (!email.trim())           newErrors["email"] = true
    if (!password.trim())        newErrors["password"] = true
    if (!confirmPassword.trim()) newErrors["confirmPassword"] = true

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }
    setErrors({})
    console.log("Form submitted")
  }

  return (
    <div className="flex flex-col justify-center px-4 sm:px-16 py-6 w-full min-h-screen bg-white">
      <div className="max-w-xl w-full mx-auto text-center">
        <h2 className="text-4xl font-semibold text-black mb-6">Registration</h2>

        <div className="space-y-4">

          {/* First & Last Name */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative group text-left">
              <span className="absolute -top-3 left-6 px-2 bg-white text-sm font-medium text-[#365885] z-10">
                First name
              </span>
              <input
                type="text"
                value={firstName}
                onChange={e => setFirstName(e.target.value)}
                className={`w-full px-6 py-3.5 rounded-[20px] border-[1.5px] ${errors["firstName"] ? "border-red-400" : "border-[#365885]/60"} hover:border-[#365885] focus:border-[#365885] focus:ring-0 transition-all outline-none text-gray-700 text-base`}
                placeholder="First name"
              />
              {errors["firstName"] && (
                <p className="text-red-400 text-xs mt-1 ml-2">This field is required</p>
              )}
            </div>
            <div className="relative group text-left">
              <span className="absolute -top-3 left-6 px-2 bg-white text-sm font-medium text-[#365885] z-10">
                Last name
              </span>
              <input
                type="text"
                value={lastName}
                onChange={e => setLastName(e.target.value)}
                className={`w-full px-6 py-3.5 rounded-[20px] border-[1.5px] ${errors["lastName"] ? "border-red-400" : "border-[#365885]/60"} hover:border-[#365885] focus:border-[#365885] focus:ring-0 transition-all outline-none text-gray-700 text-base`}
                placeholder="Last name"
              />
              {errors["lastName"] && (
                <p className="text-red-400 text-xs mt-1 ml-2">This field is required</p>
              )}
            </div>
          </div>

          {/* Email */}
          <div className="relative group">
            <span className="absolute -top-3 left-6 px-2 bg-white text-sm font-medium text-[#365885] z-10">
              Email
            </span>
            <div className="relative">
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className={`w-full pl-6 pr-14 py-3.5 rounded-[20px] border-[1.5px] ${errors["email"] ? "border-red-400" : "border-[#365885]/60"} hover:border-[#365885] focus:border-[#365885] focus:ring-0 transition-all outline-none text-gray-700 text-base`}
                placeholder="Email"
              />
              <div className="absolute right-5 top-1/2 -translate-y-1/2 text-[#365885]">
                <User size={24} />
              </div>
            </div>
            {errors["email"] && (
              <p className="text-red-400 text-xs mt-1 ml-2">This field is required</p>
            )}
          </div>

          {/* Password */}
          <div className="relative group">
            <label className="absolute -top-3 left-6 px-1.5 bg-white text-sm font-medium text-[#365885] z-10">
              Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={e => setPassword(e.target.value)}
                className={`w-full pl-6 pr-14 py-3.5 rounded-[20px] border-[1.5px] ${errors["password"] ? "border-red-400" : "border-[#365885]/60"} hover:border-[#365885] focus:border-[#365885] focus:ring-0 transition-all outline-none text-gray-700 text-base`}
                placeholder="•••••••••••"
              />
              <div
                className="absolute right-5 top-1/2 -translate-y-1/2 text-[#365885] cursor-pointer"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <Eye size={24} /> : <EyeOff size={24} />}
              </div>
            </div>
            {errors["password"] && (
              <p className="text-red-400 text-xs mt-1 ml-2">This field is required</p>
            )}
          </div>

          {/* Confirm Password */}
          <div className="relative group">
            <label className="absolute -top-3 left-6 px-1.5 bg-white text-sm font-medium text-[#365885] z-10">
              Confirm Password
            </label>
            <div className="relative">
              <input
                type={showConfirmPassword ? "text" : "password"}
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                className={`w-full pl-6 pr-14 py-3.5 rounded-[20px] border-[1.5px] ${errors["confirmPassword"] ? "border-red-400" : "border-[#365885]/60"} hover:border-[#365885] focus:border-[#365885] focus:ring-0 transition-all outline-none text-gray-700 text-base`}
                placeholder="•••••••••••"
              />
              <div
                className="absolute right-5 top-1/2 -translate-y-1/2 text-[#365885] cursor-pointer"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                {showConfirmPassword ? <Eye size={24} /> : <EyeOff size={24} />}
              </div>
            </div>
            {errors["confirmPassword"] && (
              <p className="text-red-400 text-xs mt-1 ml-2">This field is required</p>
            )}
          </div>

          {/* Account Type */}
          <div className="relative group">
            <span className="absolute -top-3 left-6 px-2 bg-white text-sm font-medium text-[#365885] z-10">
              Account type :
            </span>
            <div className="grid grid-cols-2 gap-3 animate-in slide-in-from-top duration-500">
              {["patient", "personnel médical"].map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setAccountType(type)}
                  className={`
                    w-full py-3.5 rounded-[20px] border-[1.5px] transition-all text-sm font-medium cursor-pointer capitalize flex items-center justify-center mt-4 hover:scale-105 hover:shadow-sm hover:border-[#365885] hover:bg-cyan-200/20 hover:text-[#365885] 
                    ${
                      accountType === type
                        ? "bg-[#6492C9]  border-[#365885]/60 text-white shadow-sm"
                        : "bg-white border-[#365885]/60 text-[#365885] hover:border-[#365885]"
                    }
                  `}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-4 pt-2">
            <button 
              onClick={handleSubmit}
              className="w-full py-3.5 bg-[#6492C9] hover:bg-[#537db1] text-white text-lg font-semibold rounded-[20px] transition-all duration-200 shadow-sm cursor-pointer dlowd hover:scale-105"
            >
              Continue
            </button>

            <div className="flex flex-col items-center gap-4">
              <p className="text-xs font-medium text-gray-500">
                or register with social platforms
              </p>
              <div className="flex gap-4">
                <button className="w-12 h-12 flex items-center justify-center bg-white border border-gray-200 rounded-[15px] hover:bg-gray-100 transition-all cursor-pointer shadow-sm">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="24" height="24">
                    <path fill="#0a0a0aff" d="M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.65-.389-3.917z" />
                  </svg>
                </button>
                <button className="w-12 h-12 flex items-center justify-center bg-white border border-gray-200 rounded-[15px] hover:bg-gray-100 transition-all cursor-pointer shadow-sm">
                  <Facebook size={24} fill="#000000ff" strokeWidth={0} />
                </button>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
